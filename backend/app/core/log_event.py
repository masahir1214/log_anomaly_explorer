from sqlalchemy import Column, Integer, String, DateTime, Float, Index
from app.core.database import Base

class LogEvent(Base):
    __tablename__ = "log_events"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String, index=True)
    timestamp = Column(DateTime, nullable=False)
    service = Column(String, nullable=False)
    severity = Column(String, nullable=False, default="INFO")
    message = Column(String, nullable=False)
    template_hash = Column(String, index=True)  # For semantic detection later
    trace_id = Column(String, index=True, nullable=True)

    __table_args__ = (
        Index("ix_log_events_svc_ts", "service", "timestamp"),
        Index("ix_log_events_timestamp", "timestamp"),
    )