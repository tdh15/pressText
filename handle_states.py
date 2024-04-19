# handle_states.py
# Take in the user's previous state and their most recent text and return
# the appropriate response and their new state.

import json
import txt_config
import helper as helper
import zlib

from send_articles_to_users import get_article_one_liners, send_articles_to_user

from raptor_ops import get_raptor_response

# If they've never texted before and text "news", send them the intro message
def s_000(body, session_value):
    print("handle_states.py: s_000()")
    if body.strip().lower() == 'news':
        outgoing_messages = [txt_config.s_000_intro_0, txt_config.s_000_intro_1, txt_config.s_000_intro_2, txt_config.s_000_intro_3, txt_config.s_000_question_0, txt_config.s_000_question_1, txt_config.s_000_question_2]
        next_state = "001"
        return outgoing_messages, next_state, None
    else:
        # Outgoing messages are empty if they don't text "ap"
        return [], session_value, None

# If they text one or multiple of the numbers from 1 to 4, ask them to confirm their choices.
# Otherwise, ask them to put in their response again.
def s_001(body, session_value):
    print("handle_states.py: s_001()")
    print(1)
    # Get the digits from the user's response - False if invalid, otherwise a list of digits
    selected_digits = helper.validate_preference_input(body)
    print(2)
    print(selected_digits)
    if selected_digits:
        print(3)
        # Mapping of digits to categories
        category_map = {
            '1': "US",
            '2': "World",
            '3': "Business",
            '4': "Arts"
        }
    
        # Map the selected digits to their corresponding categories
        selected_categories = [category_map[digit] for digit in selected_digits if digit in category_map]
        print(4)
        print(selected_categories)
        # Convert selected_digits to preference array format
        preference_arr = helper.convert_to_preference_array(selected_digits)
    
        # Construct the confirmation question
        confirmation_question = "You've expressed interest in the following categories: " + ", ".join(selected_categories) + ". Is this correct?"
        outgoing_messages = [confirmation_question]
        next_state = "002"
        return outgoing_messages, next_state, preference_arr
    else:
        print(5)
        outgoing_messages = [txt_config.s_001_incorrect]
        return outgoing_messages, session_value, False # False because no preference_arr
    
# If they text "yes", send them a confirmation message. If they text "no", ask them to put in their response again.
def s_002(body, session_value):
    print("handle_states.py: s_002()")
    if body.lower() in txt_config.YES_ANSWERS:
        outgoing_messages = ["Great! To receive your first set of articles, text \"articles\".", "(It may take a few minutes to receive them)"]
        next_state = "010"
        return outgoing_messages, next_state, None
    elif body.lower() in txt_config.NO_ANSWERS:
        outgoing_messages = ["Sorry, let's try that again.", txt_config.s_000_question_0, txt_config.s_000_question_1, txt_config.s_000_question_2]
        next_state = "001"
        return outgoing_messages, next_state, None
    else:
        outgoing_messages = ["Sorry, I didn't understand that. Please respond with 'yes' or 'no'."]
        return outgoing_messages, session_value, None

# Send them their articles for the first time
def s_010(body, session_value, user):
    print("handle_states.py: s_010()")
    # Send them their articles
    send_articles_to_user(user)
    # No outgoing messages because they're being sent articles via the function
    next_state = "011"
    return [], next_state, None
    
# If they've had articles sent to them, they can ask questions about them.
# They stay in this state for good.
def s_011(body, session_value, user):
    print("handle_states.py: s_011()")

    # If they text "articles", resend them the one-liners of the articles
    if body.strip().lower() == "articles" or body.strip().lower() == "article":
        # Get the one-liners of the articles
        one_liners = get_article_one_liners(json.loads(user.selected_articles))
        return one_liners, session_value, None
    else:
        # Get the user's tree
        compressed_tree = user.tree
        tree = zlib.decompress(compressed_tree)

        user_query = body

        # Get the RAPTOR response
        response = get_raptor_response(tree, user_query)

        # Construct the outgoing messages by splitting up the response into sentences
        outgoing_messages = helper.split_into_sentences(response)
        return outgoing_messages, session_value, None