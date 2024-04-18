# db/models.py
# Define tables of the database.

from sqlalchemy import Column, Integer, Float, String, Text, LargeBinary, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Note: I have no data validation. We are living fast and loose. Anything could
# be inserted into the database. This is a bad practice.

# Users
class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    phone_number = Column(String, index=True) # Indexed for fast lookup
    state = Column(String) # '000', '001', '002', etc. indicating the state of the conversation
    preferences = Column(String) # '[0, 0, 0, 0]' indicating news preferences of user
    selected_articles = Column(String) # '[2, 3, 5, 7, 14]' - the 5 article IDs of the articles that have been sent
    # Note: must be string, because ARRAY is not supported in SQLite
    tree = Column(LargeBinary) # Tree containing summary embeddings of their 5 articles from RAPTOR

    messages = relationship("Message", back_populates="user")

# Messages in the conversation between user and bot
class Message(Base):
    __tablename__ = 'messages'

    message_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    sender = Column(String) # 'user' or 'assistant'
    body = Column(String) # The message itself
    timestamp = Column(Float) # Time in UTC

    user = relationship("User", back_populates="messages")

# Current day's articles from the Associated Press
class Article(Base):
    __tablename__ = 'articles'

    article_id = Column(Integer, primary_key=True)
    category = Column(String) # 'us', 'world', 'business', or 'arts'
    title = Column(String)
    one_liner = Column(String) # First paragraph of the article with the location removed
    complete_text = Column(Text) # Full text of the article
    link = Column(String) # Link to the article