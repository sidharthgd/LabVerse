import os
import json
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

# 1. Setup paths and models
DATA_DIR = "data"
VECTOR_DB_DIR = "chroma_db"

llm = Ollama(model="mistral")
embedding_function = OllamaEmbeddings(model="mistral")

# 2. Extract metadata from files
def extract_metadata(file_path):
    ext = os.path.splitext(file_path)[1]
    try:
        if ext == ".csv":
            df = pd.read_csv(file_path)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        elif ext == ".json":
            with open(file_path) as f:
                sample = json.load(f)
                df = pd.json_normalize(sample if isinstance(sample, list) else [sample])
        else:
            return None
        columns = ', '.join(df.columns)
        return f"File: {os.path.basename(file_path)} | Columns: {columns} | Rows: {len(df)}"
    except Exception as e:
        return f"File: {os.path.basename(file_path)} | Error reading file."

# 3. Build documents for vector store
docs = []
file_map = {}

for filename in os.listdir(DATA_DIR):
    path = os.path.join(DATA_DIR, filename)
    metadata = extract_metadata(path)
    if metadata:
        docs.append(metadata)
        file_map[metadata] = path

# 4. Store embeddings in Chroma
db = Chroma.from_texts(docs, embedding_function, persist_directory=VECTOR_DB_DIR)
db.persist()

# 5. Setup Retrieval QA Chain
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=db.as_retriever(),
    chain_type="stuff"
)

# 6. Example Queries
while True:
    query = input("\nAsk LabVerse something (or type 'exit'): ")
    if query.lower() == 'exit':
        break
    answer = qa.run(query)
    print(f"\nAnswer: {answer}")
