#!/usr/bin/env python3
"""
Re-embed and re-index datasets in Pinecone
"""

import asyncio
from app.services.embeddings import EmbeddingService
from app.services.ingestion import IngestionService
from app.models.db import get_db
from app.models.documents import Document

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
