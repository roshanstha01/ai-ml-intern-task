from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import ChatRequest, ChatResponse
from app.services.booking_service import BookingService
from app.services.memory_service import RedisMemoryService
from app.services.rag_service import RAGService

router = APIRouter(tags=["Conversational RAG"])

memory_service = RedisMemoryService()
rag_service = RAGService()
booking_service = BookingService()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    try:
        history = memory_service.get_history(request.session_id)

        if booking_service.is_booking_intent(request.message):
            response_text = booking_service.save_booking(db=db, message=request.message)
        else:
            response_text = rag_service.answer_query(
                query=request.message,
                history=history,
            )

        memory_service.add_message(request.session_id, "user", request.message)
        memory_service.add_message(request.session_id, "assistant", response_text)

        return ChatResponse(
            session_id=request.session_id,
            response=response_text,
        )

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Internal server error: {error}") from error