from pydantic import BaseModel
import os

#Handy util class for Java Web Tokens
class JWTSettings(BaseModel):
    jwt_issuer: str = os.getenv("JWT_ISSUER", "auth")
    jwt_audience: str = os.getenv("JWT_AUDIENCE", "goclub")
    jwt_secret: str = os.getenv("JWT_SECRET", "rosebud")
    jwt_algorithm: str = os.getenv("JWT_ALG", "HS256")
    access_token_minutes: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "15"))
    refresh_token_days: int = int(os.getenv("REFRESH_TOKEN_DAYS", "7"))

settings = JWTSettings()