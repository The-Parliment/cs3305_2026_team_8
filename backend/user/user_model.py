from pydantic import BaseModel

class UsersRequest(BaseModel):
    inviter: str
    invitee: str
    
class UsernameRequest(BaseModel):
    username: str

class MessageResponse(BaseModel):
    message: str
    valid : bool | None = None


class UsernameListResponse(BaseModel):
    user_names: list