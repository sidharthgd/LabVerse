import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Directory configurations
DATA_DIR = "data"
VECTOR_DB_DIR = "chroma_db"

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")

# Import OpenAI models instead of Ollama
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Initialize OpenAI models
llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model="gpt-3.5-turbo",  # More cost-effective than gpt-4
    temperature=0,
    max_tokens=1000,  # Limit token usage for cost control
    timeout=30  # 30 second timeout
)

embedding_function = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model="text-embedding-3-small",  # More cost-effective embedding model
    timeout=30
)

# Optional: Model configurations for different use cases
MODEL_CONFIGS = {
    "fast": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 1000
    },
    "detailed": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 2000
    },
    "analysis": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 3000
    }
}

def get_llm_for_task(task_type="fast"):
    """Get LLM configured for specific task types."""
    config = MODEL_CONFIGS.get(task_type, MODEL_CONFIGS["fast"])
    return ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=config["model"],
        temperature=0,
        max_tokens=config["max_tokens"],
        timeout=30
    )
