from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.ingestion import IngestionService
from app.services.drive import DriveService
from app.services.box import BoxService

router = APIRouter()

@router.post("/ingest/drive")
async def ingest_google_drive(background_tasks: BackgroundTasks):
    """
    Trigger Google Drive ingestion process
    """
    try:
        drive_service = DriveService()
        ingestion_service = IngestionService()
        
        # TODO: Implement background ingestion
        background_tasks.add_task(drive_service.sync_files)
        return {"message": "Drive ingestion started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest/box")
async def ingest_box(background_tasks: BackgroundTasks):
    """
    Trigger Box ingestion process
    """
    try:
        box_service = BoxService()
        ingestion_service = IngestionService()
        
        # TODO: Implement background ingestion
        background_tasks.add_task(box_service.sync_files)
        return {"message": "Box ingestion started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
