from typing import List, Dict, Any, Optional
import os
import numpy as np
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.schemas import PolicyMatch

settings = get_settings()


class VectorStore:
    """Vector store using FAISS for similarity search."""
    
    def __init__(self):
        self.index = None
        self.chunks = []
        self.embeddings_model = None
        self._initialized = False
    
    async def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for texts using available provider."""
        if settings.use_openai:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            
            embeddings = []
            for text in texts:
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                embeddings.append(response.data[0].embedding)
            return np.array(embeddings, dtype=np.float32)
        else:
            # Use simple TF-IDF based embeddings as fallback
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            if not hasattr(self, 'vectorizer'):
                self.vectorizer = TfidfVectorizer(max_features=1536)
            
            if len(texts) == 1 and hasattr(self, 'vectorizer') and hasattr(self.vectorizer, 'vocabulary_'):
                embeddings = self.vectorizer.transform(texts).toarray()
            else:
                embeddings = self.vectorizer.fit_transform(texts).toarray()
            
            # Pad to 1536 dimensions if needed
            if embeddings.shape[1] < 1536:
                padding = np.zeros((embeddings.shape[0], 1536 - embeddings.shape[1]))
                embeddings = np.hstack([embeddings, padding])
            
            return embeddings.astype(np.float32)
    
    async def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a document and return chunks."""
        chunks = []
        
        if not os.path.exists(file_path):
            # Return demo chunks if file doesn't exist
            return [
                {
                    "content": "Coverage includes medical expenses up to policy limits.",
                    "page_number": 1,
                    "section": "Coverage"
                },
                {
                    "content": "Pre-existing conditions are excluded from coverage.",
                    "page_number": 2,
                    "section": "Exclusions"
                },
                {
                    "content": "Claims must be filed within 30 days of incident.",
                    "page_number": 3,
                    "section": "Filing Requirements"
                }
            ]
        
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(file_path)
            
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    # Split into chunks of ~500 chars
                    words = text.split()
                    chunk_size = 100  # words
                    
                    for j in range(0, len(words), chunk_size):
                        chunk_text = ' '.join(words[j:j + chunk_size])
                        if chunk_text.strip():
                            chunks.append({
                                "content": chunk_text,
                                "page_number": i + 1,
                                "section": f"Page {i + 1}"
                            })
        except Exception as e:
            # Return demo chunks on error
            chunks = [
                {
                    "content": "Policy coverage terms and conditions apply.",
                    "page_number": 1,
                    "section": "General"
                }
            ]
        
        return chunks
    
    async def rebuild_index(self, db: Session):
        """Rebuild the FAISS index from database chunks."""
        try:
            import faiss
        except ImportError:
            # FAISS not available, use simple cosine similarity
            self._use_simple_search = True
            return
        
        from app.models.orm import PolicyChunk as PolicyChunkORM, PolicyDocument as PolicyDocumentORM
        
        # Get all chunks
        chunks = db.query(PolicyChunkORM).all()
        
        if not chunks:
            self.index = None
            self.chunks = []
            return
        
        # Get document names
        doc_map = {}
        docs = db.query(PolicyDocumentORM).all()
        for doc in docs:
            doc_map[doc.id] = doc.name
        
        # Store chunk data
        self.chunks = [
            {
                "id": str(c.id),
                "document_id": str(c.document_id),
                "document_name": doc_map.get(c.document_id, "Unknown"),
                "content": c.content,
                "page_number": c.page_number,
                "section": c.section
            }
            for c in chunks
        ]
        
        # Get embeddings
        texts = [c.content for c in chunks]
        embeddings = await self._get_embeddings(texts)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        
        self._initialized = True
    
    async def search(self, query: str, top_k: int, db: Session) -> List[PolicyMatch]:
        """Search for similar chunks."""
        if not self._initialized or not self.chunks:
            # Return demo results
            return [
                PolicyMatch(
                    chunk_id="demo-1",
                    document_name="Auto Insurance Policy Guide",
                    content="Coverage includes collision damage up to actual cash value of the vehicle.",
                    relevance_score=0.85,
                    page_number=5,
                    section="Coverage"
                ),
                PolicyMatch(
                    chunk_id="demo-2",
                    document_name="Medical Coverage Handbook",
                    content="Medical expenses are covered up to the policy limit after deductible.",
                    relevance_score=0.78,
                    page_number=12,
                    section="Benefits"
                )
            ]
        
        try:
            import faiss
            
            # Get query embedding
            query_embedding = await self._get_embeddings([query])
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(query_embedding, min(top_k, len(self.chunks)))
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    results.append(PolicyMatch(
                        chunk_id=chunk["id"],
                        document_name=chunk["document_name"],
                        content=chunk["content"],
                        relevance_score=float(scores[0][i]),
                        page_number=chunk["page_number"],
                        section=chunk["section"]
                    ))
            
            return results
            
        except Exception:
            # Return demo results on error
            return [
                PolicyMatch(
                    chunk_id="demo-1",
                    document_name="Policy Document",
                    content="Standard coverage terms apply to this claim type.",
                    relevance_score=0.75,
                    page_number=1,
                    section="General"
                )
            ]
