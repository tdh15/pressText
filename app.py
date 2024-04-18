# app.py

from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
# For handling the background job of sending messages
from threading import Thread
from redis_client import RedisClient
import time
import logging

from process_messages import intake_message, process_send_queue

# The session object makes use of a secret key.
SECRET_KEY = 'a secret key'
app = Flask(__name__)
app.config.from_object(__name__)

redis_client = RedisClient.get_instance()

# Make it so Twilio doesn't print so much in the logs
twilio_logger = logging.getLogger('twilio')
twilio_logger.setLevel(logging.WARNING)

print('Starting server...');

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    # Get the message the user sent
    body = request.values.get('Body', None)
    phone_number = request.values.get('From', None)
    print()
    print(f'Incoming message from {phone_number}: \"{body}\"')
    current_time = time.time()

    # If there is currently a message (or multiple messages) that the user has
    # sent that we're working on the response for, cancel the response that's
    # being worked on, and start a new one with this message combined with the
    # previous.
    currently_processing = redis_client.get(phone_number)
    if currently_processing is not None:
        print("app.py: A message was sent while another was being processed. Combining messages.")
        currently_processing_body = currently_processing.decode('utf-8')
        # Halt the processing of the previous message in process_messages.py
        # by setting a flag in Redis
        flag = f"{current_time}_{currently_processing_body}_{phone_number}_cancel"
        redis_client.set(flag, 1)
        # Combine the newly received message with the message we were
        # processing
        combined_body = f"{currently_processing_body}|{body}"
    else:
        # If there's no message currently being processed, just use the message
        # the user sent
        combined_body = body

    # Store the combined message as the value in the key-value pair for the
    # user's phone number, so we know this is currently being processed
    redis_client.set(phone_number, combined_body)

    # If the user has texted recently (last 4 hours), we keep state in the
    # session so we can quickly retrieve it without querying the database.
    session_value = session.get('state', None)

    # Process the message, updating the session value as needed
    updated_session_value = intake_message(combined_body, phone_number, session_value, current_time)
    session['state'] = updated_session_value

    # Do not send a response - this will instead be handled by outgoing_sms()
    resp = MessagingResponse()
    return str(resp)

if __name__ == "__main__":
    # schedule_daily_tasks()
    thread = Thread(target=process_send_queue, daemon=True)
    thread.start()
    app.run(debug=True)