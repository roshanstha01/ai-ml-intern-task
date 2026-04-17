from fastapi import FastAPI

from app.api.booking import router as booking_router
from app.api.chat import router as chat_router
from app.api.document import router as document_router
from app.api.ingestion import router as ingestion_router
from app.db.database import Base, engine

app = FastAPI(title="AI/ML Intern Task API")

Base.metadata.create_all(bind=engine)

app.include_router(ingestion_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(document_router, prefix="/api")
app.include_router(booking_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "API is running"}