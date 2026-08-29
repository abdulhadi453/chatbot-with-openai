"""
Pydantic models for API requests and responses.
These match the TypeScript interfaces in the frontend.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Literal


class MessageModel(BaseModel):
    """Message model matching frontend Message interface."""
    id: str
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime
    isLoading: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "m1",
                "role": "user",
                "content": "Hello, how are you?",
                "timestamp": "2024-01-01T12:00:00Z",
                "isLoading": False
            }
        }


class ConversationModel(BaseModel):
    """Conversation model matching frontend Conversation interface."""
    id: str
    title: str
    messages: List[MessageModel]
    createdAt: datetime
    updatedAt: datetime
    preview: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "1",
                "title": "My Conversation",
                "messages": [],
                "createdAt": "2024-01-01T12:00:00Z",
                "updatedAt": "2024-01-01T12:00:00Z",
                "preview": "Hello, how are you?"
            }
        }


class CreateConversationRequest(BaseModel):
    """Request model for creating a new conversation."""
    title: Optional[str] = Field(default="New Conversation", max_length=200)


class SendMessageRequest(BaseModel):
    """Request model for sending a message."""
    content: str = Field(..., min_length=1, max_length=10000)

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Tell me about quantum computing"
            }
        }


class UpdateConversationTitleRequest(BaseModel):
    """Request model for updating conversation title."""
    title: str = Field(..., min_length=1, max_length=200)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Quantum Computing Discussion"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Conversation not found"
            }
        }
