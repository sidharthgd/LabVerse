DATA_DIR = "data"
VECTOR_DB_DIR = "chroma_db"

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama

llm = ChatOllama(model="mistral", temperature=0)
embedding_function = OllamaEmbeddings(model="mistral")
