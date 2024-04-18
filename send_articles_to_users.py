# send_articles_to_users.py
# Text one-liners of preference-based articles to all users.

import random
import json
import time

from db.client import TursoDBClient
from db.models import User, Article, Message
from add_message_to_send_queue import add_message_to_send_queue
from raptor_ops import create_tree

# select_user_articles(preferences):
# - Choose article_id of 5 articles that this user will be getting
# - Return them as an array

# Note: article_ids are such that 1-5 is us, 6-10 is world, 11-15 is business, 16-20 is arts
# So, we'll choose one number at random from each category range that the user
# has a preference for until we have 5 articles. This way we get an even distribution
# from all categories that the user has a preference for.
# Preference array is of the form "[0, 1, 0, 1]" where 0 means no preference and 1 means preference
# for that category. "us", "world", "business", "arts" respectively
def select_user_article_ids(preference_arr, num_articles=5):
    print("Selecting article ids based on user preferences")
    available_ids = []

    for index, preference in enumerate(preference_arr):
        if preference == 1:
            range_start = index * 5 + 1
            mini_internal_range = []
            for i in range(range_start, range_start + 5):
                mini_internal_range.append(i)
            available_ids.append(mini_internal_range)

    print(f"Available ids: {available_ids}")
    selected_articles = []

    while len(selected_articles) < num_articles:
        for mini_range in available_ids:
            # Pop a random id from the mini range
            article_id = random.choice(mini_range)
            selected_articles.append(article_id)
            mini_range.remove(article_id)
            if len(selected_articles) == num_articles:
                break
    print(selected_articles)
    return selected_articles

# Get the one liner of each article chosen
# Formatting: Add the number with the close parenthesis before each one liner
# Example: 1) This is the first article one liner
# Return an array of these one liners
def get_article_one_liners(selected_articles):
    print("Getting one-liners of the selected articles from db")
    session = TursoDBClient().get_session()
    one_liners = []
    count = 1
    for article_id in selected_articles:
        article = session.query(Article).filter(Article.article_id == article_id).first()
        one_liners.append(f"{count}) {article.one_liner}")
        count+=1
    session.close()
    return one_liners

# Overall individual user function(user):
# - select_user_articles(user.preferences)
# - Save selected_articles array to the User entry
# - get_article_one_liners(selected_articles)
# - Text the output of get_article_one_liners to the User
# - Add the messages being sent to the db
def send_articles_to_user(user):
    # Convert preferences string-list to list
    preference_arr = json.loads(user.preferences)
    selected_articles = select_user_article_ids(preference_arr)
    user.selected_articles = str(selected_articles)
    user.tree = create_tree(selected_articles) # Store compressed, serialized tree
    one_liners = get_article_one_liners(selected_articles)

    # Make one-liners into outgoing messages, along with intro and two additional messages
    outgoing_messages = ["Here's your news for today!", "Text back questions about the news below, and we'll do our best to answer them.", "Tip: Reference the specific article number (\"In Article 3, ...\") for better responses."]
    outgoing_messages.extend(one_liners)
    outgoing_messages.append("To have these articles sent to you again, text \"articles\" at any time.")
    
    # Text the one-liners to the user
    print("Sending one-liners to user")
    for message in outgoing_messages:
        add_message_to_send_queue(message, user.phone_number)

    # Add the messages being sent to the db
    assistant_message_send_time = time.time()
    db_session = TursoDBClient().get_session()
    combined_assistant_message = ' '.join(outgoing_messages)
    new_assistant_message = Message(user_id=user.user_id, sender='assistant', body=combined_assistant_message, timestamp=assistant_message_send_time)
    db_session.add(new_assistant_message)

    # Set user's state to 011 (they've had articles sent to them and can ask questions)
    user.state = "011"

    # Commit all DB changes from this session
    print("Committing changes to database")
    db_session.commit()
    db_session.close()

# Overall function:
# - Call individual user function on every user in the table whose preferences
# are not all 0
def send_articles_to_users():
    print("Sending articles to all users")
    session = TursoDBClient().get_session()
    users = session.query(User).all()
    sent_count = 0
    for user in users:
        # Must convert string-list to list
        # e.g. "[0, 1, 0, 1]" -> [0, 1, 0, 1]
        if 1 in json.loads(user.preferences):
            send_articles_to_user(user)
            sent_count += 1
    session.commit()
    session.close()
    print(f"Sent articles to {sent_count} users")