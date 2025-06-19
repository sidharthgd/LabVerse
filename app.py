from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from qa_agent import setup_qa
import os
import json
from typing import List, Optional
from config import DATA_DIR

app = FastAPI(title="LabVerse AI", description="Intelligent Laboratory Data Analysis Assistant")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

qa = setup_qa()   # This is your process_query function

class QueryRequest(BaseModel):
    query: str
    include_visualization: Optional[bool] = False
    export_data: Optional[bool] = False

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
        "endpoints": {
            "/chat": "POST - Send queries for data analysis",
            "/files": "GET - List available data files",
            "/upload": "POST - Upload new data files",
            "/export/{filename}": "GET - Export data files",
            "/health": "GET - Health check"
        }
    }

@app.post("/chat")
async def chat_endpoint(req: QueryRequest):
    """Enhanced chat endpoint with support for visualizations and data export."""
    try:
        # Process the query
        answer = qa(req.query)
        
        response_data = {
            "message": answer,
            "query": req.query,
            "timestamp": "2024-01-01T00:00:00Z"  # You can add proper timestamp
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
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

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
        
        # Rebuild vector store to include new file
        # This would require calling your indexing function
        # For now, we'll just return success
        
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
        "files_count": len([f for f in os.listdir(DATA_DIR) if f.endswith(('.csv', '.xlsx', '.xls', '.json', '.txt', '.tsv'))])
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
