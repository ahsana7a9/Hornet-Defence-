@router.get("/logs")
def get_logs():
    from core.elasticsearch_client import es

    res = es.search(index="threats", query={"match_all": {}})
    return res["hits"]["hits"]
# backend/api_routes.py
from fastapi import APIRouter, Depends
from core.elasticsearch_client import es
from backend.auth import verify_token  # Import the logic we put in auth.py

router = APIRouter()

# --- PUBLIC ROUTES ---
@router.get("/status")
def get_status():
    return {"status": "operational", "system": "Hornet-Defence"}

# --- PROTECTED ROUTES ---
# We add the dependency here so only authorized users can see the logs
@router.get("/logs", dependencies=[Depends(verify_token)])
def get_logs():
    """Fetches threat history from Elasticsearch (Secure)"""
    res = es.search(index="threats", query={"match_all": {}})
    return [hit["_source"] for hit in res["hits"]["hits"]]

@router.get("/secure", dependencies=[Depends(verify_token)])
def secure_test():
    """Example Number 2: A simple check to verify if a token works"""
    return {"msg": "Secure access granted to the Hornet Hive"}
