# process_messages.py

import os
from redis_client import RedisClient
from twilio.rest import Client
import json
import time

from db.client import TursoDBClient
from db.models import User, Message

from add_message_to_send_queue import add_message_to_send_queue
from send_articles_to_users import send_articles_to_user

import handle_states as handle_states

# Credentials for sending messages
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
from_number = os.environ['TWILIO_PHONE_NUMBER']
client = Client(account_sid, auth_token)

redis_client = RedisClient.get_instance()

def processing_cancellation_initiated(body, phone_number, current_time):
    # Cancellation flag must be assigned to both the phone number AND the body
    # that was being processed so we don't accidentally cancel the newer message
    # which is being processed - ran into this in testing
    flag = f"{current_time}_{body}_{phone_number}_cancel"
    if redis_client.get(flag) == b'1':
        redis_client.set(flag, 0)
        redis_client.delete(flag)  # Clear the flag
        return True
    else:
        return False

# For incoming messages, select a response and following state
def intake_message(body, phone_number, session_value, current_time):
    print(f'process_messages.py: intake_message(): Processing message: \"{body}\" from {phone_number}. Session: {session_value}')

    # Get the current user from the database, and initialize the session
    # which all DB operations for this message will take place in.
    # Note: there's two competing definitions of 'session' here - the session
    # in the database (db_session), and the session in the Flask app (session_value).
    db_session = TursoDBClient.get_session()
    print("process_messages.py: intake_message(): Accessing user from database")
    user = db_session.query(User).filter(User.phone_number == phone_number).first()
    print(f"User: {user}")
    # If the user's text is the first of this session, check if they have
    # a state stored in the database.
    # If they do, grab that state, and set current_session_value to it.
    # If they don't, they're a new user. Add them to the database with state
    # '000' and set current_session_value to '000'.

    current_session_value = session_value
    if session_value in [None, "000"]:
        print("process_messages.py: intake_message(): No session value found in Flask session for user")
        if user is not None:
            print("Accessing user's state from database")
            current_session_value = user.state
        else:
            # To avoid adding a new user who doesn't want to use the service,
            # check for "news" text
            if body.strip().lower() == 'news':
                print("Adding new user to database")
                current_session_value = "000"
                new_user = User(phone_number=phone_number, state=current_session_value, preferences='[0, 0, 0, 0]')
                db_session.add(new_user)
                db_session.commit()
                user = db_session.query(User).filter(User.phone_number == phone_number).first()
                # Immediately commit and grab the user from the database so we can use
                # their user_id in the Message table
                # We can do this now because even if they send another text, we
                # don't want to undo this operation - we want them in the Users table

    updated_session_value = None
    outgoing_messages = []

    # Check if we've initiated a cancellation (new message has been received so
    # this one should not be processed). We check this before state handling,
    # and after state handling, in case the user sent another text
    # while state handling operations were taking place.
    if processing_cancellation_initiated(body, phone_number, current_time):
        print("process_messages.py: intake_message(): Message cancellation initiated")
        return current_session_value

    # For testing, so I can go back to reset state
    if '|reset' in body.strip().lower() or body.strip().lower() == 'reset':
        current_session_value = "000"

    # Handle states
    # The third return value is for any additional value that needs to be returned.
    # In most cases, this is None. It is used for more complex
    # state handling, in which additional values need to be passed back (such as
    # the user's preferences).
    if current_session_value is None:
        outgoing_messages, updated_session_value, _ = [], None, None
    elif current_session_value == "000":
        outgoing_messages, updated_session_value, _ = handle_states.s_000(body, current_session_value)
    elif current_session_value == "001":
        outgoing_messages, updated_session_value, preference_arr = handle_states.s_001(body, current_session_value)
        # Temporarily save the user's preferences to Redis, to be added to the
        # DB if they confirm these as their preferences
        if preference_arr:
            print(f"Saving user's preference array to redis: {preference_arr}")
            redis_client.set(f"{phone_number}_preferences", json.dumps(preference_arr))
    elif current_session_value == "002":
        outgoing_messages, updated_session_value, _ = handle_states.s_002(body, current_session_value)
    elif current_session_value == "010":
        # 010 is the state where the user has confirmed their preferences,
        # but has yet to receive any articles they can ask questions about.
        # When they send a text, they'll get their first batch of articles.
        
        # Corner case: session value still has them at 010 but they've already
        # received articles --> update their state to 011
        if isinstance(user.tree, bytes):
            outgoing_messages, updated_session_value, _ = handle_states.s_011(body, "011", user)
        else:
            outgoing_messages, updated_session_value, _ = handle_states.s_010(body, current_session_value, user)
    elif current_session_value == "011":
        # 011 is the state where the user has received articles and can ask questions.
        outgoing_messages, updated_session_value, _ = handle_states.s_011(body, current_session_value, user)
    
    if processing_cancellation_initiated(body, phone_number, current_time):
        return current_session_value

    # Now that we've processed a response for the user and checked that no
    # additional message was received while we were doing it, we delete the message
    # (or multiple combined messages) that we were responding to from the Redis
    # key-value pair for their phone number.
    # We do this before sending our response messages, because this is the latest
    # in the response process that we can still be certain of exactly what has 
    # been carried out - with sending messages, the speed of the sending can vary.
    print("process_messages.py: intake_message(): Deleting message from Redis for user's phone number")
    redis_client.delete(phone_number)

    # Add outgoing_messages to queue in order
    print("process_messages.py: intake_message(): Adding messages to send queue")
    for message in outgoing_messages:
        add_message_to_send_queue(message, phone_number)

    # DB operations are handled here, only after messages have been sent.
    
    if user is not None:
        # Update the user's state in the database
        print("process_messages.py: intake_message(): Updating user's state in database")
        user.state = updated_session_value
        
        # If updated_session_value is 010, the user confirmed their preferences.
        # If the Redis tag still exists, add the preferences to the database,
        # and delete the Redis tag.
        if updated_session_value == "010":
            preference_arr = redis_client.get(f"{phone_number}_preferences")
            print(f"process_messages.py: intake_message(): preference_arr is {preference_arr}")
            if preference_arr:
                print("Adding user's preferences to database")
                user.preferences = preference_arr.decode('utf-8')
                print("Deleting redis flag for user's preferences")
                redis_client.delete(f"{phone_number}_preferences")

        new_user_message = Message(user_id=user.user_id, sender='user', body=body, timestamp=current_time)
        db_session.add(new_user_message)
        assistant_message_send_time = time.time()
        if outgoing_messages:
            combined_assistant_message = ' '.join(outgoing_messages)
            new_assistant_message = Message(user_id=user.user_id, sender='assistant', body=combined_assistant_message, timestamp=assistant_message_send_time)
            db_session.add(new_assistant_message)
    # Commit all DB changes from this session
    print("Committing changes to database")
    db_session.commit()
    db_session.close()

    # Return the updated session value if it exists, otherwise just keep it the same
    print(f"process_messages.py: intake_message(): Returning updated session value: {updated_session_value}")
    updated_session_value = updated_session_value if updated_session_value else session_value
    return updated_session_value

# Send a message
def send_message(body, phone_number):
    print(f'Sending message')
    message = client.messages.create(
        body=body,
        from_=os.environ['TWILIO_PHONE_NUMBER'],
        to=phone_number
    )
    print(f'Message sent: {message.sid}')

# Send each message in the queue
def process_send_queue():
    while True:
        try:
            # Use Redis 'brpop' to retrieve the last message from the list
            _, message_data = redis_client.brpop('send_queue')
            # The body of the message, and the phone number it's intended for,
            # is saved as one item to Redis as a json object
            message, phone_number = json.loads(message_data.decode('utf-8')).values()
            send_message(message, phone_number)
            # Wait half a second before sending the next message, so that they arrive
            # in order.
            time.sleep(0.5)
        except Exception as e:
            print(f'Error processing message: {e}')