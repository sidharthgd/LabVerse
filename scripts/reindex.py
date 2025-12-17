#!/usr/bin/env python3
"""
Re-embed and re-index datasets in Pinecone
"""

import sys
import os
from pathlib import Path

# Ensure the backend directory is in the Python path for absolute imports
backend_dir = (Path(__file__).resolve().parent.parent / "backend").resolve()
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import asyncio
from app.services.embeddings import EmbeddingService  # pyright: ignore[reportMissingImports]
from app.services.ingestion import IngestionService  # pyright: ignore[reportMissingImports]
from app.models.db import get_db  # pyright: ignore[reportMissingImports]
from app.models.documents import Document  # pyright: ignore[reportMissingImports]

async def reindex_all_documents():
    """Re-index all documents in Pinecone"""
    
    embedding_service = EmbeddingService()
    ingestion_service = IngestionService()
    
    db = next(get_db())
    
    try:
        # Get all documents
        documents = db.query(Document).all()
        
        print(f"Re-indexing {len(documents)} documents...")
        
        for doc in documents:
            print(f"Processing: {doc.filename}")
            
            # Re-create chunks and embeddings
            chunks = await ingestion_service._create_chunks(doc)
            await ingestion_service._embed_chunks(chunks)
            
            print(f"✓ Completed: {doc.filename}")
        
        print("Re-indexing completed successfully!")
        
    except Exception as e:
        print(f"Error during re-indexing: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(reindex_all_documents())
