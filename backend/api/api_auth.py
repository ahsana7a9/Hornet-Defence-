from fastapi import APIRouter
from jose import jwt
from datetime import datetime, timedelta
import os

router = APIRouter()

SECRET = os.getenv("JWT_SECRET", "shadowmesh_secret_change_in_production")

def create_token(user: str) -> str:
    payload = {
        "sub": user,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

@router.post("/auth/token")
def get_token(username: str = "admin"):
    token = create_token(username)
    return {"access_token": token, "token_type": "bearer"}
