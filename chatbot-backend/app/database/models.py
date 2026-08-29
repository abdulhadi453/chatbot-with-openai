"""
SQLAlchemy database models for persistent storage.
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Conversation(Base):
    """Conversation database model."""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    title = Column(String(200), nullable=False, default="New Conversation")
    preview = Column(String(200), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.timestamp")


class Message(Base):
    """Message database model."""
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")
