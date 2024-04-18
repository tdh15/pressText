# raptor_ops.py
# Handles creating and interacting with RAPTOR trees

print("Importing raptor, this may take a while...")
from raptor.raptor import RetrievalAugmentation
from db.client import TursoDBClient
from db.models import Article, User
import re
import zlib

# Take in array of selected article ids ([1, 2, 3, 4, 5]) and create a
# RAPTOR summary tree with them, returning serialized tree
def create_tree(selected_article_ids):
    print("Creating RAPTOR tree from selected articles")
    RA = RetrievalAugmentation()
    session = TursoDBClient().get_session()
    docs = ""
    count = 1
    for article_id in selected_article_ids:
        article = session.query(Article).filter(Article.article_id == article_id).first()
        docs += f"\n\n Article {count} text: "
        # Put the article number at the beginning of each text chunk (metadata)
        # This follows the pattern used in split_text
        # Split the text into sentences using multiple delimiters
        delimiters = [".", "!", "?", "\n"]
        regex_pattern = "|".join(map(re.escape, delimiters))
        sentences = re.split(regex_pattern, article.complete_text)
        for sentence in sentences:
            docs += f"From Article {count}: " + sentence
        # Include the link to the article at the end of the text so the user can
        # ask for it
        docs += f"\n\n Link to article {count}: " + article.link
        count+=1
    print(f"Adding articles to RAPTOR tree")
    # Must add as one long string
    RA.add_documents(docs)
    session.close()
    serialized_tree = RA.save()
    compressed_tree = zlib.compress(serialized_tree)
    return compressed_tree

# Take in serialized tree and user query, return RAPTOR response
def get_raptor_response(serialized_tree, user_query):
    print("Answering user question with RAPTOR tree")
    RA = RetrievalAugmentation(tree=serialized_tree)
    answer = RA.answer_question(question=user_query)
    return answer

# # Example usage
# session = TursoDBClient().get_session()
# user = session.query(User).filter(User.user_id == 1).first()
# session.close()
# print(get_raptor_response(user.tree, "whats up with iran"))