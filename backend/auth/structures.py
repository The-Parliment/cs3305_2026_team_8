from pydantic import BaseModel

# Requests

class RegisterRequest(BaseModel):
    username: str
    password: str
    email : str
    phone_number : str | None = None

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str
    
class UsernameRequest(BaseModel):
    username: str
    
class ResetPasswordRequest(BaseModel):
    old_password: str
    new_password: str

# Responses

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None

class MessageResponse(BaseModel):
    message: str

class UsernameResponse(BaseModel):
    username: str

class UserDetailsResponse(BaseModel):
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: str
    phone_number: str | None = None