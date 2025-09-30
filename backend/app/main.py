from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import query, files, ingest, health
from app.config import settings

app = FastAPI(
    title="LabVerse API",
    description="AI-powered data analysis platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(query.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(ingest.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "LabVerse API is running"}
