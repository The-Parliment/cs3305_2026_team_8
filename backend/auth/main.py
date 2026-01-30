import logging
from fastapi import FastAPI, HTTPException
from common.DatabaseClasses import User
from common.JWTSecurity import decode_and_verify
from security import mint_access_token, mint_refresh_token, verify_user
from structures import LoginRequest, TokenResponse, RefreshRequest

logging.basicConfig(level=logging.INFO, format='[auth] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/auth", title="auth_service")

@app.get("/")
async def root():
    return {"message: API called"}

#There is absolute no HTML served in the microservice, this returns a token
@app.post("/login", response_model=TokenResponse)
async def login(request : LoginRequest) -> TokenResponse:
    if not verify_user(request.username, request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access = mint_access_token(subject=request.username, extra_claims={"roles": ["user"]})
    refresh = mint_refresh_token(subject=request.username)

    return TokenResponse(access_token=access, refresh_token=refresh)

#This simply allows the user token to be refreshed after a long period of time
@app.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest) -> TokenResponse:
    # 1) Verify refresh token
    try:
        payload = decode_and_verify(req.refresh_token, expected_type="refresh")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # 2) Mint new access token
    access = mint_access_token(subject=payload["sub"], extra_claims={"roles": payload.get("roles", ["user"])})
    return TokenResponse(access_token=access)
