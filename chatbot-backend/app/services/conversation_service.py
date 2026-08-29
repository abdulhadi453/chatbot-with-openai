"""
Conversation service handling database operations.
Provides business logic layer between routes and database.
"""
import logging
import uuid
from datetime import datetime, UTC
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Conversation, Message
from app.models.schemas import ConversationModel, MessageModel

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversations and messages in the database."""

    @staticmethod
    def _conversation_to_model(db_conversation: Conversation) -> ConversationModel:
        """Convert database Conversation to Pydantic model."""
        messages = [
            MessageModel(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp
            )
            for msg in db_conversation.messages
        ]

        return ConversationModel(
            id=db_conversation.id,
            title=db_conversation.title,
            messages=messages,
            createdAt=db_conversation.created_at,
            updatedAt=db_conversation.updated_at,
            preview=db_conversation.preview
        )

    async def get_conversations(self, db: AsyncSession) -> List[ConversationModel]:
        """
        Retrieve all conversations ordered by most recent first.

        Args:
            db: Database session

        Returns:
            List of conversation models
        """
        try:
            result = await db.execute(
                select(Conversation)
                .options(selectinload(Conversation.messages))
                .order_by(Conversation.updated_at.desc())
            )
            conversations = result.scalars().all()

            return [self._conversation_to_model(conv) for conv in conversations]

        except Exception as e:
            logger.error(f"Error retrieving conversations: {e}")
            raise

    async def get_conversation(
        self,
        db: AsyncSession,
        conversation_id: str
    ) -> Optional[ConversationModel]:
        """
        Retrieve a single conversation by ID.

        Args:
            db: Database session
            conversation_id: Conversation identifier

        Returns:
            Conversation model or None if not found
        """
        try:
            result = await db.execute(
                select(Conversation)
                .options(selectinload(Conversation.messages))
                .where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()

            if not conversation:
                return None

            return self._conversation_to_model(conversation)

        except Exception as e:
            logger.error(f"Error retrieving conversation {conversation_id}: {e}")
            raise

    async def create_conversation(
        self,
        db: AsyncSession,
        title: str = "New Conversation"
    ) -> ConversationModel:
        """
        Create a new conversation.

        Args:
            db: Database session
            title: Conversation title

        Returns:
            Created conversation model
        """
        try:
            conversation_id = str(uuid.uuid4())
            now = datetime.now(UTC)

            conversation = Conversation(
                id=conversation_id,
                title=title,
                created_at=now,
                updated_at=now
            )

            db.add(conversation)
            await db.commit()

            logger.info(f"Created conversation: {conversation_id}")

            # Return model directly without accessing lazy-loaded relationships
            return ConversationModel(
                id=conversation_id,
                title=title,
                messages=[],  # New conversation has no messages
                createdAt=now,
                updatedAt=now,
                preview=None
            )

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating conversation: {e}")
            raise

    async def add_message(
        self,
        db: AsyncSession,
        conversation_id: str,
        role: str,
        content: str
    ) -> MessageModel:
        """
        Add a message to a conversation.

        Args:
            db: Database session
            conversation_id: Conversation identifier
            role: Message role ('user' or 'assistant')
            content: Message content

        Returns:
            Created message model
        """
        try:
            # Verify conversation exists
            result = await db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()

            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            # Check message count without accessing relationship
            count_result = await db.execute(
                select(Message).where(Message.conversation_id == conversation_id)
            )
            existing_messages = count_result.scalars().all()
            is_first_message = len(existing_messages) == 0

            # Create message
            message_id = str(uuid.uuid4())
            now = datetime.now(UTC)

            message = Message(
                id=message_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
                timestamp=now
            )

            db.add(message)

            # Update conversation timestamp and preview
            conversation.updated_at = now
            if role == "user":
                conversation.preview = content[:60]

            # Update title if this is the first message
            if is_first_message:
                conversation.title = content[:50] + ("..." if len(content) > 50 else "")

            await db.commit()

            logger.info(f"Added {role} message to conversation {conversation_id}")

            # Return model directly without accessing lazy-loaded attributes
            return MessageModel(
                id=message_id,
                role=role,
                content=content,
                timestamp=now
            )

        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error adding message: {e}")
            raise

    async def delete_conversation(
        self,
        db: AsyncSession,
        conversation_id: str
    ) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            db: Database session
            conversation_id: Conversation identifier

        Returns:
            True if deleted, False if not found
        """
        try:
            result = await db.execute(
                delete(Conversation).where(Conversation.id == conversation_id)
            )

            await db.commit()

            deleted = result.rowcount > 0
            if deleted:
                logger.info(f"Deleted conversation: {conversation_id}")
            else:
                logger.warning(f"Conversation not found for deletion: {conversation_id}")

            return deleted

        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting conversation {conversation_id}: {e}")
            raise

    async def update_conversation_title(
        self,
        db: AsyncSession,
        conversation_id: str,
        title: str
    ) -> Optional[ConversationModel]:
        """
        Update conversation title.

        Args:
            db: Database session
            conversation_id: Conversation identifier
            title: New title

        Returns:
            Updated conversation model or None if not found
        """
        try:
            result = await db.execute(
                select(Conversation)
                .options(selectinload(Conversation.messages))
                .where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()

            if not conversation:
                return None

            conversation.title = title
            conversation.updated_at = datetime.now(UTC)

            await db.commit()
            await db.refresh(conversation)

            logger.info(f"Updated title for conversation {conversation_id}")

            return self._conversation_to_model(conversation)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating conversation title: {e}")
            raise


# Global conversation service instance
conversation_service = ConversationService()
