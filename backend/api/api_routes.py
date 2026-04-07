from fastapi import APIRouter, Depends, HTTPException, status
from core.auth import verify_token
from core.elasticsearch_client import log_event, search_events

router = APIRouter()

@router.get("/status")
def get_status():
    return {"status": "operational", "system": "Hornet-Defence"}

@router.get("/logs", dependencies=[Depends(verify_token)])
def get_logs():
    """Fetches threat history from Elasticsearch (Secure)"""
    try:
        hits = search_events("threats")
        return hits
    except Exception as e:
        return {"error": str(e), "logs": []}

@router.get("/logs/public")
def get_logs_public():
    """Public endpoint returning recent threats (no auth required)"""
    try:
        hits = search_events("threats")
        return hits
    except Exception:
        return []

@router.get("/secure", dependencies=[Depends(verify_token)])
def secure_test():
    return {"msg": "Secure access granted to the Hornet Hive"}
