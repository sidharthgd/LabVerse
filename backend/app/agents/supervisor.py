from typing import Dict, Any
from app.agents.rag_agent import RAGAgent
from app.agents.pandas_agent import PandasAgent
from app.agents.sql_agent import SQLAgent
from app.agents.utils import classify_query

class Supervisor:
    """
    Decides which agent to use based on query type
    """
    
    def __init__(self):
        self.rag_agent = RAGAgent()
        self.pandas_agent = PandasAgent()
        self.sql_agent = SQLAgent()
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route query to appropriate agent
        """
        query_type = classify_query(query)
        
        if query_type == "rag":
            return await self.rag_agent.process(query, context)
        elif query_type == "pandas":
            return await self.pandas_agent.process(query, context)
        elif query_type == "sql":
            return await self.sql_agent.process(query, context)
        else:
            # Default to RAG for general queries
            return await self.rag_agent.process(query, context)
