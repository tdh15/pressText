# ap/add_articles_to_db.py
# Add AP articles to the database, replacing those which were previously there.

# Note: to run this, I had to use `python3 -m ap.add_articles_to_db`, because
# the import statements were not working properly. The `-m` makes it work properly.
from db.client import TursoDBClient
from db.models import Article
from helper import find_first_sentence

def add_articles_to_db(ap_data):
    print("Commencing updating articles in the database.")

    # Get the session
    session = TursoDBClient().get_session()

    print("Deleting all articles from the database.")
    # Delete all articles from the database
    session.query(Article).delete()

    # Add the new articles
    for category, articles in ap_data.items():
        for article_url, article_data in articles.items():
            title = article_data[0]
            content = article_data[1]
            one_liner = find_first_sentence(content)

            print(f"Adding article to DB: {title}")
            article = Article(category=category, title=title, one_liner=one_liner, complete_text=content, link=article_url)
            session.add(article)

    print("Committing session")
    # Commit the changes
    session.commit()

    print("Closing session")
    # Close the session
    session.close()

# Example usage

# # Get fresh AP articles and add them all to the database
# from ap.get_ap_data import get_ap_data
# ap_data = get_ap_data()
# add_articles_to_db(ap_data)
# print("Articles added to the database.")
    
# # Print the info of each article in the database
# counter = 1
# session = TursoDBClient().get_session()
# articles = session.query(Article).all()
# for article in articles:
#     print(counter)
#     print(f"category: {article.category}")
#     print(f"title: {article.title}")
#     print()
#     counter += 1
# session.close()