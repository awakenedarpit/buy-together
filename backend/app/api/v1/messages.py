"""Message ingestion and personal message history endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.schemas.message import MessageCreate, MessageResponse, MessageOut, RequestItemOut
from backend.app.services.message_service import MessageService
from backend.app.ai.exceptions import AIProviderError
from backend.app.core.logging import logger

router = APIRouter(tags=["messages"])
message_service = MessageService()


@router.post(
    "/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit natural language request message",
)
@router.post(
    "/messages/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def submit_message(
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Submit a natural language message for AI item extraction and persistence.
    
    1. Authenticates current user.
    2. Validates message text.
    3. Runs extraction through AIProvider and Pydantic validation pipeline.
    4. Atomically persists Message and extracted RequestItems.
    """
    clean_text = payload.text.strip()
    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message text cannot be empty or only whitespace.",
        )

    try:
        message, items = await message_service.create_message_and_extract_items(
            db=db,
            user=current_user,
            text=clean_text,
        )
    except AIProviderError as ai_err:
        logger.error(f"[API] AI extraction failed for user {current_user.id}: {ai_err}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI extraction provider error: {str(ai_err)}",
        )
    except Exception as exc:
        logger.error(f"[API] Failed processing message: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the message.",
        )

    return MessageResponse(
        message=MessageOut.model_validate(message),
        extracted_items=[RequestItemOut.model_validate(item) for item in items],
    )


@router.get(
    "/messages",
    response_model=List[MessageOut],
    status_code=status.HTTP_200_OK,
    summary="List authenticated user's message history",
)
@router.get(
    "/messages/",
    response_model=List[MessageOut],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def list_my_messages(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[MessageOut]:
    """Retrieve message history for the currently authenticated member.
    
    Enforces strict ownership: members can only inspect their own submitted messages.
    """
    messages = message_service.get_user_messages(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return [MessageOut.model_validate(msg) for msg in messages]
