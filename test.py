# test.py

# Test everything together
# get_ap_data
# prep_preferred_articles
# process_messages

from ap.get_ap_data import get_ap_data
from prep_preferred_articles import process_preference_array
from process_messages import add_message_to_send_queue
import time
import json

from db.client import TursoDBClient
from db.models import Article

# preference_arr = [0, 0, 0, 1]
# ap_data = get_ap_data()
# preferred_articles = process_preference_array(preference_arr, ap_data)
# counter = 0
# for article_title, article_string in preferred_articles.items():
#     counter+=1
#     message_str = (f"{counter}) {article_string}")
#     add_message_to_send_queue(message_str, +13035948479)
#     time.sleep(1)

# add_message_to_send_queue("Hello, this is a test message", +19493711982)

# session = TursoDBClient().get_session()
# article = session.query(Article).filter(Article.article_id == 1).first()
# print(article.title)

# Decode something with utf-8 using json
to_decode = json.dumps("WyIyIiwgIjMiXQ==").decode('utf-8')
print(to_decode)
