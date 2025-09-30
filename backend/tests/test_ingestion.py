import pytest
from app.services.ingestion import IngestionService

class TestIngestionService:
    def test_ingestion_service_initialization(self):
        service = IngestionService()
        assert service is not None
    
    @pytest.mark.asyncio
    async def test_process_file(self):
        service = IngestionService()
        # TODO: Add test file content
        result = await service.process_file("test.txt", b"test content")
        assert result is not None