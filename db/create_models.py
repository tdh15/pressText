# db/create_models.py
# One-time script to create the database models (tables).

import os

# Note: to run this, I had to use `python3 -m db.create_models`, because
# the import statements were not working properly. The `-m` makes it work properly.
from db.models import Base, User
from sqlalchemy import create_engine

# Get environment variables
TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

# Construct special SQLAlchemy URL
dbUrl = f"sqlite+{TURSO_DATABASE_URL}/?authToken={TURSO_AUTH_TOKEN}&secure=true"

print("Creating tables...")

engine = create_engine(dbUrl, connect_args={'check_same_thread': False}, echo=True)

Base.metadata.create_all(engine)

print("Tables created.")