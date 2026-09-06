from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.parsing.registry import detect_and_parse
from app.services.ingestion.ingest import bulk_insert_events
import uuid

router = APIRouter(prefix="/api/logs", tags=["logs"])

@router.post("/upload")
async def upload_logs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    lines = contents.decode("utf-8").splitlines()
    
    if not lines:
        raise HTTPException(status_code=400, detail="Empty file")
        
    dataset_id = f"ds_{uuid.uuid4().hex[:8]}"
    
    try:
        parsed_events = detect_and_parse(lines, dataset_id)
        bulk_insert_events(db, parsed_events)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
        
    return {
        "dataset_id": dataset_id,
        "parsed_count": len(parsed_events),
        "status": "success"
    }
