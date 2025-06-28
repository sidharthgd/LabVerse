"""
Hybrid Retriever for LabVerse Agent

Combines semantic search with metadata filtering for optimal data retrieval.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import os
from langchain_community.vectorstores import Chroma
from langchain.schema import Document


class RetrievalResult(BaseModel):
    """Result of data retrieval."""
    documents: List[Dict[str, Any]]
    file_paths: List[str]
    metadata: Dict[str, Any]
    confidence: float


class Retriever:
    """
    Hybrid retriever that combines semantic search with metadata filtering.
    
    Uses:
    - ChromaDB for semantic search
    - Metadata filtering for file types, columns, project tags
    - Context-aware ranking
    """
    
    def __init__(self, vector_db: Chroma, data_dir: str):
        self.vector_db = vector_db
        self.data_dir = data_dir
        self.retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    
    def retrieve_context(self, 
                        query: str,
                        entities: Dict[str, Any],
                        filters: Optional[Dict[str, Any]] = None,
                        max_results: int = 3) -> RetrievalResult:
        """
        Retrieve relevant context for the query.
        
        Args:
            query: User query string
            entities: Extracted entities from the query
            filters: Optional metadata filters
            max_results: Maximum number of results to return
            
        Returns:
            RetrievalResult with relevant documents and metadata
        """
        # Step 1: Semantic search
        semantic_docs = self._semantic_search(query, max_results * 2)  # Get more for filtering
        
        # Step 2: Apply entity-based filtering
        filtered_docs = self._apply_entity_filters(semantic_docs, entities)
        
        # Step 3: Apply metadata filters
        if filters:
            filtered_docs = self._apply_metadata_filters(filtered_docs, filters)
        
        # Step 4: Rank and select top results
        ranked_docs = self._rank_documents(filtered_docs, query, entities)
        final_docs = ranked_docs[:max_results]
        
        # Step 5: Load additional metadata
        enriched_docs = self._enrich_documents(final_docs)
        
        # Step 6: Calculate confidence
        confidence = self._calculate_retrieval_confidence(enriched_docs, query, entities)
        
        return RetrievalResult(
            documents=enriched_docs,
            file_paths=[doc["file_path"] for doc in enriched_docs],
            metadata=self._aggregate_metadata(enriched_docs),
            confidence=confidence
        )
    
    def _semantic_search(self, query: str, k: int) -> List[Document]:
        """Perform semantic search using ChromaDB."""
        try:
            return self.retriever.get_relevant_documents(query)[:k]
        except Exception as e:
            print(f"Semantic search failed: {e}")
            return []
    
    def _apply_entity_filters(self, docs: List[Document], entities: Dict[str, Any]) -> List[Document]:
        """Filter documents based on extracted entities."""
        if not entities:
            return docs
        
        filtered_docs = []
        
        # Filter by file entities
        file_entities = entities.get("files", [])
        if file_entities:
            for doc in docs:
                file_name = doc.metadata.get("file_name", "")
                if any(entity.lower() in file_name.lower() for entity in file_entities):
                    filtered_docs.append(doc)
            # If no exact matches, keep all documents
            if not filtered_docs:
                filtered_docs = docs
        else:
            filtered_docs = docs
        
        # Filter by column entities
        column_entities = entities.get("columns", [])
        if column_entities:
            column_filtered = []
            for doc in filtered_docs:
                doc_columns = doc.metadata.get("columns", "").lower()
                if any(entity.lower() in doc_columns for entity in column_entities):
                    column_filtered.append(doc)
            # If no column matches, keep the file-filtered results
            if column_filtered:
                filtered_docs = column_filtered
        
        return filtered_docs
    
    def _apply_metadata_filters(self, docs: List[Document], filters: Dict[str, Any]) -> List[Document]:
        """Apply metadata-based filters."""
        filtered_docs = []
        
        for doc in docs:
            include_doc = True
            
            # File type filter
            if "file_type" in filters:
                file_path = doc.metadata.get("file_path", "")
                file_extension = os.path.splitext(file_path)[1].lower()
                if file_extension not in filters["file_type"]:
                    include_doc = False
            
            # Date range filter
            if "date_range" in filters and "modified_date" in doc.metadata:
                # Implementation for date filtering
                pass
            
            # Size filter
            if "max_size" in filters and "file_size" in doc.metadata:
                if doc.metadata["file_size"] > filters["max_size"]:
                    include_doc = False
            
            if include_doc:
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def _rank_documents(self, docs: List[Document], query: str, entities: Dict[str, Any]) -> List[Document]:
        """Rank documents by relevance."""
        if not docs:
            return docs
        
        scored_docs = []
        
        for doc in docs:
            score = 0.0
            
            # Base semantic similarity score (from ChromaDB)
            score += 0.5
            
            # Boost for exact entity matches
            file_name = doc.metadata.get("file_name", "").lower()
            columns = doc.metadata.get("columns", "").lower()
            
            # File name match boost
            file_entities = entities.get("files", [])
            for entity in file_entities:
                if entity.lower() in file_name:
                    score += 0.3
            
            # Column match boost
            column_entities = entities.get("columns", [])
            for entity in column_entities:
                if entity.lower() in columns:
                    score += 0.2
            
            # Recency boost (if available)
            if "modified_date" in doc.metadata:
                # More recent files get slight boost
                score += 0.1
            
            scored_docs.append((doc, score))
        
        # Sort by score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_docs]
    
    def _enrich_documents(self, docs: List[Document]) -> List[Dict[str, Any]]:
        """Enrich documents with additional metadata."""
        enriched_docs = []
        
        for doc in docs:
            file_path = doc.metadata.get("file_path")
            enriched_doc = {
                "file_path": file_path,
                "file_name": doc.metadata.get("file_name", ""),
                "description": doc.page_content,
                "columns": doc.metadata.get("columns", "").split(", ") if doc.metadata.get("columns") else [],
                "metadata": doc.metadata.copy()
            }
            
            # Add file statistics if available
            if file_path and os.path.exists(file_path):
                try:
                    stat = os.stat(file_path)
                    enriched_doc["file_size"] = stat.st_size
                    enriched_doc["modified_date"] = stat.st_mtime
                except:
                    pass
            
            # Add sample data preview
            enriched_doc["sample_data"] = self._get_sample_data(file_path)
            
            enriched_docs.append(enriched_doc)
        
        return enriched_docs
    
    def _get_sample_data(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get sample data from file for context."""
        if not file_path or not os.path.exists(file_path):
            return None
        
        try:
            import pandas as pd
            
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, nrows=3)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, nrows=3)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path, lines=True, nrows=3)
            else:
                return None
            
            return {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.to_dict(),
                "sample_rows": df.head(2).to_dict('records')
            }
        except Exception as e:
            print(f"Error getting sample data from {file_path}: {e}")
            return None
    
    def _aggregate_metadata(self, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate metadata across retrieved documents."""
        if not docs:
            return {}
        
        # Collect all columns
        all_columns = set()
        file_types = set()
        total_size = 0
        
        for doc in docs:
            all_columns.update(doc.get("columns", []))
            
            file_path = doc.get("file_path", "")
            if file_path:
                file_types.add(os.path.splitext(file_path)[1].lower())
                total_size += doc.get("file_size", 0)
        
        return {
            "total_files": len(docs),
            "unique_columns": list(all_columns),
            "file_types": list(file_types),
            "total_size_bytes": total_size,
            "column_count": len(all_columns)
        }
    
    def _calculate_retrieval_confidence(self, docs: List[Dict[str, Any]], query: str, entities: Dict[str, Any]) -> float:
        """Calculate confidence in retrieval results."""
        if not docs:
            return 0.0
        
        confidence = 0.6  # Base confidence
        
        # Boost for entity matches
        entity_matches = 0
        total_entities = sum(len(v) for v in entities.values() if isinstance(v, list))
        
        if total_entities > 0:
            for doc in docs:
                file_name = doc.get("file_name", "").lower()
                columns = [c.lower() for c in doc.get("columns", [])]
                
                # Check file entity matches
                for file_entity in entities.get("files", []):
                    if file_entity.lower() in file_name:
                        entity_matches += 1
                
                # Check column entity matches
                for column_entity in entities.get("columns", []):
                    if any(column_entity.lower() in col for col in columns):
                        entity_matches += 1
            
            # Calculate entity match ratio
            match_ratio = min(1.0, entity_matches / total_entities)
            confidence += match_ratio * 0.3
        
        # Boost for multiple relevant documents
        if len(docs) >= 2:
            confidence += 0.1
        
        return min(1.0, confidence) 