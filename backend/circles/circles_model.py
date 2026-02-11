from pydantic import BaseModel

class CircleRequest(BaseModel):
    inviter: str
    invitee: str

class MessageResponse(BaseModel):
    message: str

class UsernameListResponse(BaseModel):
    user_names: list