import json
import redis
from typing import Any
import os
import dotenv
dotenv.load_dotenv()

REDIS_URL = (
    os.getenv("REDIS_URL")
    or os.getenv("LOCAL_REDIS_URL")
    or os.getenv("REMOTE_REDIS_URL")
    or "redis://localhost:6379"
)
    
r = redis.Redis.from_url(f"{REDIS_URL}/2")
DEFAULT_TTL = 3600  # 1 hour

def _key(file_id: str, name: str, version: int = 1) -> str:
    return f"resume:{file_id}:{name}:v{version}"

# -------- PDF --------
def store_pdf(file_id: str, pdf_bytes: bytes, ttl: int = DEFAULT_TTL):
    r.setex(_key(file_id, "cv_pdf"), ttl, pdf_bytes)


def load_pdf(file_id: str) -> bytes:
    data = r.get(_key(file_id, "cv_pdf"))
    if not data:
        raise KeyError("PDF expired or missing")
    return data


# -------- Extracted Text --------
def store_extracted_text(file_id: str, text: str, ttl: int = DEFAULT_TTL):
    r.setex(_key(file_id, "text"), ttl, text)


def load_extracted_text(file_id: str) -> str:
    data = r.get(_key(file_id, "text"))
    if not data:
        raise KeyError("Extracted text missing")
    
    if isinstance(data, bytes):
        return data.decode("utf-8")

    return data


# -------- Analysis Results --------
def store_analysis(file_id: str, name: str, data: Any, ttl: int = DEFAULT_TTL):
    r.setex(_key(file_id, f"analysis:{name}"), ttl, json.dumps(data))


def load_analysis(file_id: str, name: str) -> Any:
    data = r.get(_key(file_id, f"analysis:{name}"))
    if not data:
        raise KeyError(f"{name} analysis missing")
    return json.loads(data)

# -------- Final Report --------
def store_final_report(file_id: str, report: dict, ttl: int = DEFAULT_TTL):
    r.setex(_key(file_id, "final"), ttl, json.dumps(report))


def load_final_report(file_id: str) -> dict:
    data = r.get(_key(file_id, "final"))
    if not data:
        raise KeyError("Final report missing")
    return json.loads(data)
