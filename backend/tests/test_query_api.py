import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestQueryAPI:
    def test_query_endpoint(self):
        response = client.post("/api/v1/query", json={"query": "test query"})
        assert response.status_code == 200
    
    def test_files_endpoint(self):
        response = client.get("/api/v1/files")
        assert response.status_code == 200
    
    def test_health_endpoint(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
