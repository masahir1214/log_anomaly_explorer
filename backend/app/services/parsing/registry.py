import json
from dateutil import parser as date_parser
from typing import List, Dict, Any

class BaseParser:
    def can_parse(self, sample_lines: List[str]) -> float:
        raise NotImplementedError
    def parse(self, lines: List[str], dataset_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

class JSONParser(BaseParser):
    def can_parse(self, sample_lines: List[str]) -> float:
        valid_json = 0
        for line in sample_lines:
            try:
                json.loads(line)
                valid_json += 1
            except ValueError:
                pass
        return valid_json / len(sample_lines) if sample_lines else 0.0

    def parse(self, lines: List[str], dataset_id: str) -> List[Dict[str, Any]]:
        events = []
        for line in lines:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                
                # Parse timestamp and securely strip timezone for SQLite compatibility
                raw_ts = data.get("timestamp", data.get("time"))
                dt = date_parser.parse(raw_ts)
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                    
                events.append({
                    "dataset_id": dataset_id,
                    "timestamp": dt,
                    "service": data.get("service", data.get("app", "unknown")),
                    "severity": str(data.get("severity", data.get("level", "INFO"))).upper(),
                    "message": data.get("message", data.get("msg", "")),
                    "trace_id": data.get("trace_id", data.get("req_id")),
                    "template_hash": "pending_normalization" 
                })
            except Exception:
                continue
        return events

def detect_and_parse(lines: List[str], dataset_id: str) -> List[Dict[str, Any]]:
    parsers = [JSONParser()]
    sample = lines[:10]
    
    best_parser = None
    best_score = 0.0
    
    for p in parsers:
        score = p.can_parse(sample)
        if score > best_score:
            best_score = score
            best_parser = p
            
        if best_score < 0.3 or not best_parser:
            raise ValueError("Unrecognized log format")
            
    return best_parser.parse(lines, dataset_id)
