from typing import List, Dict, Any, Tuple
import openai
from pinecone import Pinecone
from app.config import settings

class EmbeddingService:
    """
    Wrapper for embedding generation + Pinecone indexing
    """

    def __init__(self):
        # Ensure API keys are present; raise clear error if missing
        if not settings.OPENAI_API_KEY:
            raise ValueError("Missing OpenAI API key. Set OPENAI_API_KEY in your environment or .env file.")
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        # Pinecone may be optional during local dev; only initialize if api key exists
        if settings.PINECONE_API_KEY:
            self.pinecone = Pinecone(api_key=settings.PINECONE_API_KEY)
            self.index = self.pinecone.Index(settings.PINECONE_INDEX_NAME)
        else:
            self.pinecone = None
            self.index = None

    def embed_text(self, text: str) -> Tuple[List[float], str]:
        """
        Generate an embedding vector for the given text using OpenAI API.
        """
        response = self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        # The response.data is a list of embedding objects; get the first one
        embedding = response.data[0].embedding
        return (embedding, text)

    def embed_batch(self, texts: List[str]) -> List[Tuple[List[float], str]]:
        print("embedding batch")
        embeddings = []
        for text in texts:
            embedding = self.embed_text(text)
            embeddings.append(embedding)
            print("embedded text", text)
        print("done embedding batch")
        return embeddings

    def store_embeddings(self, embeddings: List[Dict[str, Any]]):
        # enumerate for vector id order, change to doc_id: index later
        vectors = []
        count = 0
        for i, embedding in enumerate(embeddings):
            vectors.append({
                "id": str(i),
                "values": embedding[0],
                "metadata": {"text": embedding[1]}
            })
        try:
            print("upserting embeddings")
            count += 1
            self.index.upsert(vectors=vectors)
        except Exception as e:
            print(f"Error during Pinecone upsert: {e}")

    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar embeddings in Pinecone"""
        if not self.index:
            raise ValueError("Pinecone index is not initialized.")
        try:
            response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            print("length of response", len(response['matches']))
            # Each match in response['matches'] contains 'id', 'score', and 'metadata'
            results = []
            for match in response['matches']:
                results.append({
                    "id": match['id'],
                    "score": match['score'],
                    "metadata": match.get('metadata', {})
                })
            return results
        except Exception as e:
            print(f"Error during Pinecone similarity search: {e}")
            return []
