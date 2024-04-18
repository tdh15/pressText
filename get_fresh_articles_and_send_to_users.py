# get_fresh_articles_and_send_to_users.py
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