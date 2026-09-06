from sqlalchemy.orm import Session
from app.models.log_event import LogEvent
from typing import List, Dict, Any

def bulk_insert_events(db: Session, events_data: List[Dict[str, Any]], chunk_size: int = 5000):
    """Executemany chunked inserts for optimal WAL performance."""
    for i in range(0, len(events_data), chunk_size):
        chunk = events_data[i:i + chunk_size]
        db.bulk_insert_mappings(LogEvent, chunk)
    db.commit()