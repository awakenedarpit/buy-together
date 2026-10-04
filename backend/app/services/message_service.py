"""Message Service

Orchestrates message persistence, invokes the ExtractionService, and saves
resulting RequestItems in an atomic database transaction.
"""

from typing import List, Tuple, Optional
from sqlalchemy.orm import Session, joinedload
from backend.app.models.user import User
from backend.app.models.message import Message
from backend.app.models.request_item import RequestItem, ItemStatus
from backend.app.services.extraction_service import ExtractionService
from backend.app.schemas.ai import ExtractedItem
from backend.app.core.logging import logger


class MessageService:
    """Service handling message storage and atomic item creation."""

    def __init__(self, extraction_service: Optional[ExtractionService] = None):
        self.extraction_service = extraction_service or ExtractionService()

    async def create_message_and_extract_items(
        self,
        db: Session,
        user: User,
        text: str,
    ) -> Tuple[Message, List[RequestItem]]:
        """Persist user message, extract items via AI, and persist validated items atomically.
        
        Args:
            db: Active database session.
            user: Authenticated User submitting the request.
            text: Raw input text.
            
        Returns:
            Tuple of (Message, List[RequestItem]).
            
        Raises:
            Exception: If database commit fails or provider error occurs.
        """
        clean_text = text.strip()

        # Step 1: Run AI extraction and business validation first
        # This ensures we don't commit a message if extraction fails or throws an unhandled error
        validated_items: List[ExtractedItem] = await self.extraction_service.extract_and_validate(clean_text)

        # Step 2: Atomic database persistence
        try:
            # Create Message record
            message = Message(
                user_id=user.id,
                text=clean_text,
            )
            db.add(message)
            db.flush()  # Populates message.id without committing

            created_items: List[RequestItem] = []
            for item in validated_items:
                req_item = RequestItem(
                    message_id=message.id,
                    user_id=user.id,
                    name=item.name,
                    variant=item.variant,
                    quantity=item.quantity,
                    unit=item.unit,
                    unit_price=None,  # Prices are never set by AI or member
                    status=ItemStatus.PENDING,
                )
                db.add(req_item)
                created_items.append(req_item)

            db.commit()
            db.refresh(message)
            for req_item in created_items:
                db.refresh(req_item)

            logger.info(
                f"[MessageService] Saved message {message.id} with {len(created_items)} items for user {user.id}"
            )
            return message, created_items

        except Exception as exc:
            db.rollback()
            logger.error(f"[MessageService] Transaction failed, rolled back: {exc}")
            raise

    def get_user_messages(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Message]:
        """Fetch messages owned by the authenticated user with preloaded request items.
        
        Strict ownership enforcement: filter by user_id ensures members never see other users' messages.
        """
        return (
            db.query(Message)
            .options(joinedload(Message.request_items))
            .filter(Message.user_id == user_id)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
