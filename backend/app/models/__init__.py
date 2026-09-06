from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
import sqlite3
from sqlalchemy import event

os.makedirs("./data", exist_ok=True)
DATABASE_URL = "sqlite:///./data/log_explorer.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    status = Column(String, default="OPEN")
    start_time = Column(String)
    end_time = Column(String)
    service_count = Column(Integer)
    anomaly_count = Column(Integer)
    graph_data = Column(JSON)
    raw_anomalies = Column(JSON)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
