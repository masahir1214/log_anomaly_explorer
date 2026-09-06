import pytest
from app.services.parsing.registry import detect_and_parse

def test_json_parser_valid():
    lines = [
        '{"timestamp": "2026-01-01T12:00:00Z", "service": "auth", "severity": "ERROR", "message": "Failed to login", "trace_id": "abc-123"}',
        '{"time": "2026-01-01T12:01:00Z", "app": "db", "level": "warn", "msg": "Slow query"}'
    ]
    events = detect_and_parse(lines, "test-dataset")
    
    assert len(events) == 2
    assert events[0]["service"] == "auth"
    assert events[0]["severity"] == "ERROR"
    assert events[0]["message"] == "Failed to login"
    assert events[0]["trace_id"] == "abc-123"
    
    assert events[1]["service"] == "db"
    assert events[1]["severity"] == "WARN"

def test_json_parser_malformed_and_missing_fields():
    lines = [
        '{"timestamp": "2026-01-01T12:00:00Z", "message": "Missing service"}',
        'This is not JSON at all and should be skipped',
        '{"timestamp": "invalid-date", "service": "api"}'
    ]
    
    events = detect_and_parse(lines, "test-dataset")
    assert len(events) == 1
    assert events[0]["service"] == "unknown"
    assert events[0]["message"] == "Missing service"

def test_detect_and_parse_empty():
    with pytest.raises(ValueError, match="Unrecognized log format"):
        detect_and_parse([], "test-dataset")
