from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from landingai_ade import LandingAIADE
import mimetypes
from pathlib import Path
from app.services.embeddings import EmbeddingService
from app.services.storage import StorageService
from app.models.documents import Document
from app.models.chunks import Chunk
from app.config import settings

class IngestionService:
    
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.storage_service = StorageService()
        self.landingai_client = LandingAIADE(apikey=settings.LANDINGAI_API_KEY)
    
    async def process_file(self, filename: str, file_content: bytes, user_id: Optional[str] = None) -> Document:
        
        mime_type = self._detect_mime_type(filename)
        file_size = len(file_content)
        
        #can change this, not necessary to store the entire file
        storage_path = await self.storage_service.store_file(filename, file_content, user_id)
        
        file_metadata = self._extract_file_metadata(filename, mime_type, file_size, user_id)
        
        document = Document(
            filename=filename,
            storage_path=storage_path,
            file_metadata=file_metadata,
            file_size=file_size,
            mime_type=mime_type,
            total_chunks=0
        )
        self.db.add(document)
        self.db.flush()
        
        parsed_chunks = await self._parse_file(filename, file_content, mime_type)
        
        document.total_chunks = len(parsed_chunks)
        
        chunk_records = await self._create_chunk_records(document, parsed_chunks)
        
        await self._embed_and_store_chunks(chunk_records, document)
        
        self.db.commit()
        self.db.refresh(document)
        
        return document
    
    async def _parse_file(self, filename: str, content: bytes, mime_type: str) -> List[Dict[str, Any]]:
        
        if mime_type in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return await self._parse_with_landingai(content)
        elif mime_type == 'text/plain':
            return await self._parse_text_file(content)
        else:
            raise ValueError(f"Unsupported file type: {mime_type}")
    
    async def _parse_with_landingai(self, content: bytes) -> List[Dict[str, Any]]:
        
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            response = self.landingai_client.parse(
                document_url=tmp_path,
                model="dpt-1"
            )
            
            chunks = []
            for idx, chunk in enumerate(response.chunks):
                chunk_text = chunk.markdown.strip()
                
                if not chunk_text or len(chunk_text) < 10:
                    continue
                
                chunk_data = {
                    'index': idx,
                    'text': chunk_text,
                    'page_number': getattr(chunk, 'page_number', None),
                    'metadata': {}
                }
                chunks.append(chunk_data)
            
            return chunks
        
        finally:
            os.unlink(tmp_path)
    
    async def _parse_text_file(self, content: bytes) -> List[Dict[str, Any]]:
        
        text = content.decode('utf-8')
        
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        for idx, paragraph in enumerate(paragraphs):
            if len(paragraph) < 10:
                continue
            
            chunks.append({
                'index': idx,
                'text': paragraph,
                'page_number': None,
                'metadata': {}
            })
        
        return chunks
    
    async def _create_chunk_records(self, document: Document, parsed_chunks: List[Dict[str, Any]]) -> List[Chunk]:
        
        chunk_records = []
        
        for chunk_data in parsed_chunks:
            chunk = Chunk(
                document_id=document.id,
                content=chunk_data['text'],
                chunk_index=chunk_data['index'],
                page_number=chunk_data.get('page_number'),
                chunk_metadata=chunk_data.get('metadata', {})
            )
            self.db.add(chunk)
            chunk_records.append(chunk)
        
        self.db.flush()
        
        return chunk_records
    
    async def _embed_and_store_chunks(self, chunks: List[Chunk], document: Document):
        
        vectors = []
        
        for chunk in chunks:
            enriched_text = self._enrich_chunk_text(chunk, document)
            
            embedding, _ = self.embedding_service.embed_text(enriched_text)
            
            pinecone_id = f"doc_{document.id}_chunk_{chunk.id}"
            chunk.pinecone_id = pinecone_id
            
            preview = chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
            
            vector = {
                "id": pinecone_id,
                "values": embedding,
                "metadata": {
                    "chunk_id": chunk.id,
                    "document_id": document.id,
                    "filename": document.filename,
                    "chunk_index": chunk.chunk_index,
                    "page_number": chunk.page_number,
                    "content_preview": preview,
                    "mime_type": document.mime_type
                }
            }
            vectors.append(vector)
        
        if vectors:
            self.embedding_service.index.upsert(vectors=vectors)
    
    def _enrich_chunk_text(self, chunk: Chunk, document: Document) -> str:
        
        parts = [f"Document: {document.filename}"]
        
        if chunk.page_number:
            parts.append(f"Page: {chunk.page_number}")
        
        parts.append(f"Content: {chunk.content}")
        
        return " | ".join(parts)
    
    def _detect_mime_type(self, filename: str) -> str:
        
        mime_type, _ = mimetypes.guess_type(filename)
        
        if mime_type:
            return mime_type
        
        ext = Path(filename).suffix.lower()
        mime_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain'
        }
        
        return mime_map.get(ext, 'application/octet-stream')
    
    def _extract_file_metadata(self, filename: str, mime_type: str, file_size: int, user_id: Optional[str]) -> Dict[str, Any]:
        
        return {
            "original_filename": filename,
            "file_extension": Path(filename).suffix,
            "mime_type": mime_type,
            "file_size_bytes": file_size,
            "uploaded_by": user_id,
            "processing_status": "completed"
        }
