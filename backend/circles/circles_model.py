from pydantic import BaseModel

class InviteRequest(BaseModel):
    inviter: str
    invitee: str

class InviteResponse(BaseModel):
    invite_id: int
    status: str

class GetResponse(BaseModel):
    invite_ids: list

class InviteActionRequest(BaseModel):
    invite_id: int

class AcceptResponse(BaseModel):
    circle_id: int

class MessageResponse(BaseModel):
    message: str

class ViewCircleResponse(BaseModel):
    user_names: list