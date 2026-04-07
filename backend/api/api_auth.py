from jose import jwt
from datetime import datetime, timedelta

SECRET = "shadowmesh_secret"

def create_token(user):
    payload = {
        "sub": user,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")
