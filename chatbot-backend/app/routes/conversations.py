"""
API routes for conversation management and chat functionality.
Integrates AgentService and ConversationService.
"""
import logging
import json
import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.schemas import (
    ConversationModel,
    MessageModel,
    CreateConversationRequest,
    SendMessageRequest,
    UpdateConversationTitleRequest,
    ErrorResponse
)
from app.services.agent_service import agent_service
from app.services.conversation_service import conversation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["conversations"])


@router.get(
    "/conversations",
    response_model=List[ConversationModel],
    summary="Get all conversations",
    description="Retrieve all conversations ordered by most recent first"
)
async def get_conversations(db: AsyncSession = Depends(get_db)):
    """Get all conversations with their messages."""
    try:
        conversations = await conversation_service.get_conversations(db)
        return conversations
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationModel,
    summary="Get a specific conversation",
    description="Retrieve a conversation by its ID with all messages",
    responses={404: {"model": ErrorResponse}}
)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation by ID."""
    try:
        conversation = await conversation_service.get_conversation(db, conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )

        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )


@router.post(
    "/conversations",
    response_model=ConversationModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation",
    description="Create a new empty conversation"
)
async def create_conversation(
    request: CreateConversationRequest = CreateConversationRequest(),
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation."""
    try:
        conversation = await conversation_service.create_conversation(
            db,
            title=request.title
        )
        return conversation
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageModel,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message",
    description="Send a user message and receive AI response",
    responses={404: {"model": ErrorResponse}}
)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to the AI agent and get a response.

    This endpoint:
    1. Saves the user message to the database
    2. Generates AI response using the Agent SDK
    3. Saves the assistant response to the database
    4. Returns the assistant message
    """
    try:
        # Verify conversation exists
        conversation = await conversation_service.get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )

        # Save user message to database
        user_message = await conversation_service.add_message(
            db,
            conversation_id,
            role="user",
            content=request.content
        )

        # Generate AI response using Agent SDK
        # The SDK automatically maintains conversation history via SQLiteSession
        try:
            ai_response = await agent_service.generate_response(
                conversation_id,
                request.content
            )
        except Exception as e:
            logger.error(f"Agent error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate AI response"
            )

        # Save assistant message to database
        assistant_message = await conversation_service.add_message(
            db,
            conversation_id,
            role="assistant",
            content=ai_response
        )

        return assistant_message

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.post(
    "/conversations/{conversation_id}/messages/stream",
    summary="Send a message with streaming response",
    description="Send a user message and receive AI response in real-time via Server-Sent Events",
    responses={404: {"model": ErrorResponse}}
)
async def send_message_stream(
    conversation_id: str,
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to the AI agent and stream the response in real-time.

    This endpoint:
    1. Saves the user message to the database
    2. Streams AI response using Server-Sent Events (SSE)
    3. Saves the complete assistant response to the database
    4. Returns real-time chunks as they're generated

    Response format: Server-Sent Events (SSE)
    - Each chunk: data: {"content": "text chunk"}\n\n
    - User message: data: {"type": "user_message", "message": {...}}\n\n
    - Complete message: data: {"type": "done", "message": {...}}\n\n
    - Error: data: {"type": "error", "detail": "error message"}\n\n
    """

    async def generate_stream():
        """Generator for SSE streaming."""
        try:
            # Verify conversation exists
            conversation = await conversation_service.get_conversation(db, conversation_id)
            if not conversation:
                error_data = json.dumps({"type": "error", "detail": f"Conversation {conversation_id} not found"})
                yield f"data: {error_data}\n\n"
                return

            # Save user message to database
            user_message = await conversation_service.add_message(
                db,
                conversation_id,
                role="user",
                content=request.content
            )

            # Send user message confirmation
            user_msg_data = json.dumps({
                "type": "user_message",
                "message": {
                    "id": user_message.id,
                    "role": user_message.role,
                    "content": user_message.content,
                    "timestamp": user_message.timestamp.isoformat()
                }
            })
            yield f"data: {user_msg_data}\n\n"

            # Stream AI response
            full_response = ""
            async for chunk in agent_service.generate_response_streamed(
                conversation_id,
                request.content
            ):
                full_response += chunk
                chunk_data = json.dumps({"type": "chunk", "content": chunk})
                yield f"data: {chunk_data}\n\n"

            # Save complete assistant message to database
            assistant_message = await conversation_service.add_message(
                db,
                conversation_id,
                role="assistant",
                content=full_response
            )

            # Send completion message
            done_data = json.dumps({
                "type": "done",
                "message": {
                    "id": assistant_message.id,
                    "role": assistant_message.role,
                    "content": assistant_message.content,
                    "timestamp": assistant_message.timestamp.isoformat()
                }
            })
            yield f"data: {done_data}\n\n"

        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            error_data = json.dumps({"type": "error", "detail": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation",
    description="Delete a conversation and all its messages",
    responses={404: {"model": ErrorResponse}}
)
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation and all associated messages."""
    try:
        deleted = await conversation_service.delete_conversation(db, conversation_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )


@router.patch(
    "/conversations/{conversation_id}/title",
    response_model=ConversationModel,
    summary="Update conversation title",
    description="Update the title of a conversation",
    responses={404: {"model": ErrorResponse}}
)
async def update_conversation_title(
    conversation_id: str,
    request: UpdateConversationTitleRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update conversation title."""
    try:
        conversation = await conversation_service.update_conversation_title(
            db,
            conversation_id,
            request.title
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )

        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation title: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update conversation title"
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if the API is running"
)
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "chatbot-backend"}
