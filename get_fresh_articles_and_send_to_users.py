# get_fresh_articles_and_send_to_users.py
# Daily script to re-scrape the articles from the Associated Press, add them
# to the database and 1)send one-liners to users based on their preferences, 2)
# create the per-user RAPTOR tree from the articles.

from ap.get_ap_data import get_ap_data
from ap.add_articles_to_db import add_articles_to_db
from send_articles_to_users import send_articles_to_users

def get_fresh_articles_and_send_to_users():
    ap_data = get_ap_data()
    add_articles_to_db(ap_data)
    print("Articles added to the database.")
    send_articles_to_users()

# Run when script is called
get_fresh_articles_and_send_to_users()