import jwt
from jwt import PyJWTError
from .JWTSettings import settings

#Checks that JWT is valid
def decode_and_verify(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except PyJWTError as e:
        raise ValueError(f"Invalid token: {e}") from e

    if payload.get("typ") != expected_type:
        raise ValueError("Wrong token type")
    return payload