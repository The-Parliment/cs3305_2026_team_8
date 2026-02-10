from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from common.db.db import get_db
from common.db.structures.structures import User
import jwt
from common.JWTSettings import settings
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _now() -> datetime:
    return datetime.now(timezone.utc)

#This uses PyJWT to create an authorized JWT, issued by the auth microservice.
def mint_access_token(subject: str, extra_claims: dict | None = None) -> str:
    payload = {
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "sub": subject,
        "iat": int(_now().timestamp()),
        "exp": int((_now() + timedelta(minutes=settings.access_token_minutes)).timestamp()),
        "typ": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


#This issues a refresh token, which is sort of like a long-term cached token
def mint_refresh_token(subject: str) -> str:
    payload = {
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "sub": subject,
        "iat": int(_now().timestamp()),
        "exp": int((_now() + timedelta(days=settings.refresh_token_days)).timestamp()),
        "typ": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def verify_user(username: str, password: str) -> bool:
    db = get_db()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    return pwd.verify(password, user.hashed_password)