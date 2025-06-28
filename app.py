from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from typing import List, Optional
from config import DATA_DIR

# Import with error handling
try:
    from qa_agent import setup_qa
    qa = setup_qa()
    print("✅ QA system initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize QA system: {e}")
    print("💡 Please check your OpenAI API key in .env file")
    qa = None

# Import new agent architecture
try:
    from labverse.agent.assistant_agent import AssistantAgent
    from vector_store import build_vector_store
    from config import llm
    import asyncio
    
    # Initialize the new agent
    vector_db = build_vector_store(DATA_DIR)
    available_files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.csv', '.xlsx', '.xls', '.json', '.txt', '.tsv'))]
    
    assistant_agent = AssistantAgent(
        llm=llm,
        vector_db=vector_db,
        data_dir=DATA_DIR,
        available_files=available_files
    )
    print("✅ Assistant Agent initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Assistant Agent: {e}")
    assistant_agent = None

app = FastAPI(title="LabVerse AI", description="Intelligent Laboratory Data Analysis Assistant")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    include_visualization: Optional[bool] = False
    export_data: Optional[bool] = False

class AssistantQueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    context: Optional[dict] = None

class FileUploadResponse(BaseModel):
    message: str
    filename: str
    file_path: str

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "LabVerse AI - Intelligent Laboratory Data Analysis",
        "version": "1.0.0",
        "ai_status": "Ready" if qa is not None else "Not Available - Check OpenAI API Key",
        "assistant_status": "Ready" if assistant_agent is not None else "Not Available",
        "endpoints": {
            "/chat": "POST - Send queries for data analysis (Legacy)",
            "/assistant/query": "POST - Send queries to the new agent architecture",
            "/files": "GET - List available data files",
            "/upload": "POST - Upload new data files",
            "/export/{filename}": "GET - Export data files",
            "/health": "GET - Health check"
        }
    }

@app.post("/assistant/query")
async def assistant_query_endpoint(req: AssistantQueryRequest):
    """New agent architecture endpoint."""
    if assistant_agent is None:
        raise HTTPException(
            status_code=503,
            detail="Assistant Agent not available. Please check your configuration."
        )
    
    try:
        # Process query through the agent pipeline
        response = await assistant_agent.run_query(
            query=req.query,
            session_id=req.session_id,
            context=req.context
        )
        
        # Convert to API response format
        return {
            "message": response.message,
            "code": response.code,
            "execution_result": response.execution_result,
            "code_type": response.code_type,
            "attachments": response.attachments,
            "follow_up_suggestions": response.follow_up_suggestions,
            "query": req.query,
            "session_id": req.session_id,
            "intent": response.intent,
            "entities": response.entities,
            "clarification_needed": response.clarification_needed,
            "confidence": response.confidence,
            "processing_time": response.processing_time,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/chat")
async def chat_endpoint(req: QueryRequest):
    """Enhanced chat endpoint with OpenAI integration."""
    if qa is None:
        raise HTTPException(
            status_code=503, 
            detail="QA system not available. Please check your OpenAI API key configuration in the .env file."
        )
    
    try:
        # Process the query - now returns a structured response
        qa_response = qa(req.query)
        
        # Handle the structured response
        if isinstance(qa_response, dict):
            response_data = {
                "message": qa_response.get("message", "Analysis completed"),
                "code": qa_response.get("code"),
                "execution_result": qa_response.get("execution_result"),
                "code_type": qa_response.get("code_type", "python"),
                "query": req.query,
                "timestamp": "2024-01-01T00:00:00Z"  # You can add proper timestamp
            }
        else:
            # Fallback for string responses
            response_data = {
                "message": str(qa_response),
                "code": None,
                "execution_result": None,
                "code_type": None,
                "query": req.query,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        
        # Add visualization if requested
        if req.include_visualization and "plot" in req.query.lower():
            # This would integrate with your visualization generation
            response_data["plot_url"] = "/static/plots/latest_plot.png"
            response_data["plot_filename"] = "analysis_plot.png"
        
        # Add data export if requested
        if req.export_data:
            # This would integrate with your data export functionality
            response_data["data_export"] = "sample,data,export\n1,value1,value2"
            response_data["data_filename"] = "exported_data.csv"
        
        return response_data
        
    except Exception as e:
        error_detail = str(e)
        if "api key" in error_detail.lower():
            error_detail = "OpenAI API key not configured or invalid"
        elif "rate limit" in error_detail.lower():
            error_detail = "Rate limit exceeded. Please try again in a moment"
        elif "insufficient_quota" in error_detail.lower():
            error_detail = "OpenAI API quota exceeded"
        
        raise HTTPException(status_code=500, detail=f"Error processing query: {error_detail}")

@app.get("/files")
async def list_files():
    """List all available data files with metadata."""
    try:
        files = []
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(('.csv', '.xlsx', '.xls', '.json', '.txt', '.tsv')):
                file_path = os.path.join(DATA_DIR, filename)
                file_stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "path": file_path,
                    "size": file_stat.st_size,
                    "modified": file_stat.st_mtime,
                    "type": filename.split('.')[-1].upper()
                })
        
        return {"files": [f["filename"] for f in files], "file_details": files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a new data file for analysis."""
    try:
        # Validate file type
        allowed_extensions = {'.csv', '.xlsx', '.xls', '.json', '.txt', '.tsv'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_extension} not supported. Allowed: {allowed_extensions}"
            )
        
        # Save file to data directory
        file_path = os.path.join(DATA_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update agent with new files
        if assistant_agent:
            available_files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.csv', '.xlsx', '.xls', '.json', '.txt', '.tsv'))]
            assistant_agent.update_available_files(available_files)
        
        return FileUploadResponse(
            message=f"File {file.filename} uploaded successfully",
            filename=file.filename,
            file_path=file_path
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.get("/export/{filename}")
async def export_file(filename: str):
    """Export a data file."""
    try:
        file_path = os.path.join(DATA_DIR, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting file: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "data_directory": DATA_DIR,
        "files_count": len([f for f in os.listdir(DATA_DIR) if f.endswith(('.csv', '.xlsx', '.xls', '.json', '.txt', '.tsv'))]),
        "qa_system": "ready" if qa is not None else "unavailable",
        "assistant_agent": "ready" if assistant_agent is not None else "unavailable"
    }

@app.get("/stats")
async def get_stats():
    """Get statistics about the data and system."""
    try:
        stats = {
            "total_files": 0,
            "file_types": {},
            "total_rows": 0,
            "total_columns": 0,
            "data_sources": []
        }
        
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(('.csv', '.xlsx', '.xls', '.json', '.txt', '.tsv')):
                stats["total_files"] += 1
                file_type = filename.split('.')[-1].upper()
                stats["file_types"][file_type] = stats["file_types"].get(file_type, 0) + 1
                stats["data_sources"].append(filename)
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

# Session management endpoints for the new agent
@app.get("/assistant/sessions")
async def list_sessions():
    """List active sessions."""
    if assistant_agent is None:
        raise HTTPException(status_code=503, detail="Assistant Agent not available")
    
    return {
        "active_sessions": assistant_agent.list_active_sessions(),
        "count": len(assistant_agent.list_active_sessions())
    }

@app.get("/assistant/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get session information."""
    if assistant_agent is None:
        raise HTTPException(status_code=503, detail="Assistant Agent not available")
    
    session_info = assistant_agent.get_session_info(session_id)
    if session_info is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session_info

@app.delete("/assistant/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific session."""
    if assistant_agent is None:
        raise HTTPException(status_code=503, detail="Assistant Agent not available")
    
    assistant_agent.clear_session(session_id)
    return {"message": f"Session {session_id} cleared successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
