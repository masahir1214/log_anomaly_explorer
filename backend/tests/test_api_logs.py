import io
from app.models.log_event import LogEvent

def test_upload_logs_success(client, db_session):
    log_content = (
        b'{"timestamp": "2026-01-01T12:00:00Z", "service": "api", "message": "test 1"}\n'
        b'{"timestamp": "2026-01-01T12:00:01Z", "service": "api", "message": "test 2"}\n'
    )
    
    response = client.post(
        "/api/logs/upload", 
        files={"file": ("test.log", io.BytesIO(log_content), "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["parsed_count"] == 2
    assert "dataset_id" in data
    
    db_events = db_session.query(LogEvent).all()
    assert len(db_events) == 2
    assert db_events[0].dataset_id == data["dataset_id"]

def test_upload_empty_file(client):
    response = client.post(
        "/api/logs/upload", 
        files={"file": ("empty.log", io.BytesIO(b""), "text/plain")}
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Empty file"
