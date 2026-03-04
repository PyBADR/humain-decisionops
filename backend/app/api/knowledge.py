from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID, uuid4
import os
import aiofiles
from datetime import datetime
import time

from app.models.database import get_db
from app.models.orm import PolicyDocument as PolicyDocumentORM, PolicyChunk as PolicyChunkORM
from app.models.schemas import PolicyDocument, PolicyMatch, KnowledgeTestResponse
from app.config import get_settings
from app.services.vector_store import VectorStore

router = APIRouter()
settings = get_settings()
vector_store = VectorStore()


@router.get("/documents", response_model=List[dict])
async def list_policy_documents(db: Session = Depends(get_db)):
    """List all policy documents."""
    docs = db.query(PolicyDocumentORM).all()
    return [
        {
            "id": str(d.id),
            "name": d.name,
            "filename": d.filename,
            "file_type": d.file_type,
            "indexed": d.indexed,
            "chunk_count": d.chunk_count,
            "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
            "indexed_at": d.indexed_at.isoformat() if d.indexed_at else None
        }
        for d in docs
    ]


@router.post("/upload", response_model=dict)
async def upload_policy_document(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a policy document."""
    # Save file
    os.makedirs(settings.policy_dir, exist_ok=True)
    file_path = os.path.join(settings.policy_dir, file.filename)
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Create document record
    doc = PolicyDocumentORM(
        id=uuid4(),
        name=name,
        filename=file.filename,
        file_type=file.content_type or "application/pdf",
        storage_path=file_path,
        indexed=False,
        chunk_count=0
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    return {
        "id": str(doc.id),
        "name": doc.name,
        "filename": doc.filename,
        "message": "Document uploaded successfully. Run rebuild to index."
    }


@router.post("/rebuild", response_model=dict)
async def rebuild_index(db: Session = Depends(get_db)):
    """Rebuild the vector index for all policy documents."""
    docs = db.query(PolicyDocumentORM).all()
    
    total_chunks = 0
    for doc in docs:
        # Read and chunk document
        try:
            chunks = await vector_store.process_document(doc.storage_path)
            
            # Delete existing chunks
            db.query(PolicyChunkORM).filter(
                PolicyChunkORM.document_id == doc.id
            ).delete()
            
            # Insert new chunks
            for i, chunk in enumerate(chunks):
                chunk_record = PolicyChunkORM(
                    id=uuid4(),
                    document_id=doc.id,
                    content=chunk["content"],
                    page_number=chunk.get("page_number"),
                    section=chunk.get("section")
                )
                db.add(chunk_record)
            
            doc.indexed = True
            doc.chunk_count = len(chunks)
            doc.indexed_at = datetime.utcnow()
            total_chunks += len(chunks)
            
        except Exception as e:
            doc.indexed = False
            doc.chunk_count = 0
    
    db.commit()
    
    # Rebuild FAISS index
    await vector_store.rebuild_index(db)
    
    return {
        "status": "success",
        "documents_processed": len(docs),
        "total_chunks": total_chunks
    }


@router.post("/test", response_model=KnowledgeTestResponse)
async def test_retrieval(
    query: str = Form(...),
    top_k: int = Form(5),
    db: Session = Depends(get_db)
):
    """Test retrieval with a query."""
    start_time = time.time()
    
    results = await vector_store.search(query, top_k, db)
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    return KnowledgeTestResponse(
        query=query,
        results=results,
        latency_ms=latency_ms
    )


@router.get("/status", response_model=dict)
async def get_index_status(db: Session = Depends(get_db)):
    """Get the current index status."""
    docs = db.query(PolicyDocumentORM).all()
    indexed_docs = [d for d in docs if d.indexed]
    total_chunks = sum(d.chunk_count for d in docs)
    
    return {
        "total_documents": len(docs),
        "indexed_documents": len(indexed_docs),
        "total_chunks": total_chunks,
        "index_ready": len(indexed_docs) > 0
    }
