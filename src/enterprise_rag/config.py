"""Small environment-based configuration layer; no third-party dotenv dependency required."""
from dataclasses import dataclass
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}

@dataclass(frozen=True)
class Settings:
    data_path: Path = ROOT / os.getenv("DATA_PATH", "data/synthetic_flightradar24.csv")
    sqlite_path: Path = ROOT / os.getenv("SQLITE_PATH", "data/rag.sqlite3")
    require_api_key: bool = _bool("REQUIRE_API_KEY", False)
    api_key: str = os.getenv("API_KEY", "")
    enable_ollama: bool = _bool("ENABLE_OLLAMA", False)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3.5:4b")
    ollama_timeout_seconds: float = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30"))
    retrieval_top_k: int = max(1, min(30, int(os.getenv("RETRIEVAL_TOP_K", "8"))))
    crag_max_retries: int = max(0, min(3, int(os.getenv("CRAG_MAX_RETRIES", "2"))))
    self_rag_max_revisions: int = max(0, min(2, int(os.getenv("SELF_RAG_MAX_REVISIONS", "1"))))

settings = Settings()
