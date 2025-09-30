import pytest
from app.agents.supervisor import Supervisor
from app.agents.rag_agent import RAGAgent
from app.agents.pandas_agent import PandasAgent

class TestSupervisor:
    def test_supervisor_initialization(self):
        supervisor = Supervisor()
        assert supervisor is not None
    
    @pytest.mark.asyncio
    async def test_process_query(self):
        supervisor = Supervisor()
        result = await supervisor.process_query("test query")
        assert result is not None

class TestRAGAgent:
    def test_rag_agent_initialization(self):
        agent = RAGAgent()
        assert agent is not None
    
    @pytest.mark.asyncio
    async def test_process_query(self):
        agent = RAGAgent()
        result = await agent.process("test query")
        assert result["type"] == "rag"

class TestPandasAgent:
    def test_pandas_agent_initialization(self):
        agent = PandasAgent()
        assert agent is not None
    
    @pytest.mark.asyncio
    async def test_process_query(self):
        agent = PandasAgent()
        result = await agent.process("analyze data")
        assert result["type"] == "pandas"
