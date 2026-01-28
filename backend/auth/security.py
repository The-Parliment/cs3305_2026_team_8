from datetime import datetime, timedelta, timezone
import jwt
from common.JWTSettings import settings
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

#THIS MUST BE REPLACED WITH CALL TO USER MANAGEMENT SERVICE FOR DATABASE REQUEST
_EXAMPLE_USERS = {
    "admin" : pwd.hash("admin"),
}

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
    hashed = _EXAMPLE_USERS.get(username)
    if not hashed:
        return False
    return pwd.verify(password, hashed)