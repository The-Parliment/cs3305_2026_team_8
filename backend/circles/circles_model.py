from pydantic import BaseModel

class UsersRequest(BaseModel):
    inviter: str
    invitee: str

class MessageResponse(BaseModel):
    message: str
    valid : bool | None = True

class UsernameListResponse(BaseModel):
    user_names: list