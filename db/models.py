from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Email(Base):
    __tablename__ = 'emails'

    id = Column(String, primary_key=True)  # Email ID
    from_address = Column(String)  # 'From' field
    to_address = Column(String)  # 'To' field
    subject = Column(String)  # Email subject
    date_received = Column(DateTime)  # Date when the email was received
