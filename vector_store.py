from langchain_community.vectorstores import Chroma
import os
from langchain.schema import Document
from config import VECTOR_DB_DIR, embedding_function
from indexer import scan_directory

def build_vector_store(data_dir):
    if os.path.exists(VECTOR_DB_DIR):
        print("🔹 Loading existing vector store...")
        db = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embedding_function)
    else:
        print("⚡ No vector store found. Building new one...")
        metadata_list = scan_directory(data_dir)
        
        # Create Document objects with page_content and metadata
        documents = []
        for meta in metadata_list:
            print("embedding file: ", meta["path"])
            doc = Document(
                page_content=meta["description"],
                metadata={
                    "file_path": meta["path"],
                    "file_name": meta["file"],
                    "columns": ", ".join(meta["columns"]),    # Convert list to string
                    # Remove raw_metadata to avoid complex structures
                }
            )

            documents.append(doc)
        
        db = Chroma.from_documents(
            documents, 
            embedding_function, 
            persist_directory=VECTOR_DB_DIR
        )
        db.persist()
    return db