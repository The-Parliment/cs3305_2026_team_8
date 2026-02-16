from pydantic import BaseModel

class UsersRequest(BaseModel):
    inviter: str
    invitee: str

class MessageResponse(BaseModel):
    message: str

class UsernameListResponse(BaseModel):
    user_names: list