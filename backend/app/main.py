from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.models import get_db, Incident
from app.ml_engine import process_logs_pipeline
from app.llm_engine import generate_real_rca

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI(title="Log Anomaly Explorer - Real Implementation")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.post("/api/logs/upload")
async def upload_real_logs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    # 'utf-8-sig' removes hidden Windows BOM characters automatically
    lines = contents.decode("utf-8-sig").splitlines()
    
    try:
        # Safely pass filename to the pipeline
        safe_filename = file.filename if file.filename else ""
        result = process_logs_pipeline(lines, safe_filename)
        
        new_incident = Incident(
            title=result["title"],
            severity=result["severity"],
            start_time=datetime.utcnow().isoformat(),
            end_time=datetime.utcnow().isoformat(),
            service_count=result["service_count"],
            anomaly_count=result["anomaly_count"],
            graph_data=result["graph_data"],
            raw_anomalies=result["raw_anomalies"]
        )
        db.add(new_incident)
        db.commit()
        db.refresh(new_incident)
        
        return {"dataset_id": new_incident.id, "parsed_count": len(lines), "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/incidents")
def get_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.id.desc()).all()

@app.get("/api/incidents/{incident_id}/graph")
def get_graph(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident or not incident.graph_data:
        raise HTTPException(status_code=404, detail="Graph not found")
    return incident.graph_data

@app.post("/api/incidents/{incident_id}/rca")
async def get_rca(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident or incident.raw_anomalies is None:
        raise HTTPException(status_code=404, detail="Incident data not found")
        
    rca_result = await generate_real_rca(incident.raw_anomalies)
    return rca_result
