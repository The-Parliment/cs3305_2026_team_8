from fastapi import Header, HTTPException
from .JWTSecurity import decode_and_verify

'''
Everything in this file is for managing permissions gifted by the auth microservice
but in the frontend. It still maintains the separation of frontend from backend
'''

def require_access_claims(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    try:
        return decode_and_verify(token, expected_type="access")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
