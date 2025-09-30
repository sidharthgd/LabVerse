import pytest
from app.agents.supervisor import Supervisor
from app.agents.utils import classify_query

class TestSupervisor:
    def test_classify_query_sql(self):
        query = "SELECT * FROM users WHERE age > 25"
        result = classify_query(query)
        assert result == "sql"
    
    def test_classify_query_pandas(self):
        query = "Create a bar chart showing sales by month"
        result = classify_query(query)
        assert result == "pandas"
    
    def test_classify_query_rag(self):
        query = "What is the meaning of life?"
        result = classify_query(query)
        assert result == "rag"
    
    @pytest.mark.asyncio
    async def test_supervisor_routing(self):
        supervisor = Supervisor()
        
        # Test SQL routing
        result = await supervisor.process_query("SELECT * FROM table")
        assert result["type"] == "sql"
        
        # Test Pandas routing
        result = await supervisor.process_query("analyze the data")
        assert result["type"] == "pandas"
