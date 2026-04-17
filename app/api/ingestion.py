from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Document
from app.schemas import DocumentIngestionResponse
from app.services.chunking import chunk_text
from app.services.document_parser import extract_text, validate_file_extension
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import QdrantVectorStore

router = APIRouter(tags=["Document Ingestion"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

embedding_service = EmbeddingService()
vector_store = QdrantVectorStore()


@router.post("/ingest", response_model=DocumentIngestionResponse)
def ingest_document(
    file: UploadFile = File(...),
    chunking_strategy: str = Form(...),
    db: Session = Depends(get_db),
) -> DocumentIngestionResponse:
    try:
        file_extension = validate_file_extension(file.filename)

        if chunking_strategy.lower() not in {"fixed", "paragraph"}:
            raise HTTPException(
                status_code=400,
                detail="Invalid chunking strategy. Use 'fixed' or 'paragraph'."
            )

        unique_filename = f"{uuid.uuid4()}{file_extension}"
        saved_file_path = UPLOAD_DIR / unique_filename

        with saved_file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extracted_text = extract_text(str(saved_file_path), file_extension)
        chunks = chunk_text(extracted_text, chunking_strategy)

        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks were created from the document.")

        document = Document(
            filename=file.filename,
            file_type=file_extension,
            chunking_strategy=chunking_strategy.lower(),
            total_chunks=len(chunks),
            raw_text=extracted_text,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        embeddings = embedding_service.embed_texts(chunks)

        vector_store.upsert_chunks(
            document_id=document.id,
            filename=document.filename,
            strategy=document.chunking_strategy,
            chunks=chunks,
            embeddings=embeddings,
        )

        return DocumentIngestionResponse(
            document_id=document.id,
            filename=document.filename,
            file_type=document.file_type,
            chunking_strategy=document.chunking_strategy,
            total_chunks=document.total_chunks,
            message="Document ingested successfully."
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Internal server error: {error}") from error