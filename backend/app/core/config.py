from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    DATABASE_URL: str = "sqlite:///./data/log_explorer.db"
    LLM_PROVIDER: str = "mock"
    LLM_API_KEY: str = ""
    EMBEDDING_MODEL: str = "tfidf"
    ANOMALY_THRESHOLD: float = 3.5
    ISOLATION_FOREST_CONTAMINATION: float = 0.02
    STATISTICAL_WEIGHT: float = 0.30
    ML_WEIGHT: float = 0.25
    SEMANTIC_WEIGHT: float = 0.20
    SEVERITY_WEIGHT: float = 0.15
    TEMPORAL_WEIGHT: float = 0.10
    TIME_BUCKET_SECONDS: int = 60

settings = Settings()
