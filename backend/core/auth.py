import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

# Move your secret to a config or env file later!
SECRET = "your_super_secret_key" 
security = HTTPBearer()

def verify_token(token=Depends(security)):
    try:
        # Decode the token sent in the Authorization header
        payload = jwt.decode(token.credentials, SECRET, algorithms=["HS256"])
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
