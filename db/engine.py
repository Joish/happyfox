import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

# Use env variables for sensitive data
# Ideally the username and pwd should come from secret manager
DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://happyfox:happyfox@localhost/happyfox_interview')

engine = create_engine(
    DATABASE_URI,
    pool_recycle=3600,  # Recycle connections after one hour
    pool_pre_ping=True,  # Check if connection is alive and reestablish it if necessary
    echo=False,  # Turn off echo to reduce verbosity in logs
    poolclass=NullPool  # Use NullPool for connection pooling (adjust based on your use case)
)

# Use scoped_session for thread-safe session management
Session = scoped_session(sessionmaker(bind=engine))
