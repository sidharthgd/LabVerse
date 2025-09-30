from fastapi import APIRouter, HTTPException
from app.schemas.query import QueryRequest, QueryResponse
from app.agents.supervisor import Supervisor

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_data(request: QueryRequest):
    """
    Route user query to appropriate agent via Supervisor
    """
    try:
        supervisor = Supervisor()
        result = await supervisor.process_query(request.query, request.context)
        return QueryResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
