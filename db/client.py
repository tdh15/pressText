# db/client.py
# Singleton pattern for Turso DB client, to ensure there's only one engine
# shared across the application.

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Get environment variables
TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

# Construct special SQLAlchemy URL
dbUrl = f"sqlite+{TURSO_DATABASE_URL}/?authToken={TURSO_AUTH_TOKEN}&secure=true"

class TursoDBClient:
    _instance = None
    _session_factory = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = create_engine(dbUrl, connect_args={'check_same_thread': False}, echo=False)
            cls._session_factory = sessionmaker(bind=cls._instance)
        return cls._instance

    @classmethod
    def get_session(cls):
        # Ensure the engine is initialized
        cls.get_instance()
        # Return a new session object from the factory
        return cls._session_factory()

# Usage
    
# session = TursoDBClient.get_session()
# article = session.query(Article).filter(Article.article_id == 1).first()
# print(article.title)
    