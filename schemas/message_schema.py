from pydantic import BaseModel
from datetime import datetime
from schemas.user_schema import UserShow


class MessageBase(BaseModel):
   
    title:str
    content:str
    created_at:datetime





class MessageShow(MessageBase):
    id:int
    user_sender:UserShow
    user_reciber:UserShow


class MessageList(BaseModel):
    messages: list[MessageShow]

    total_messages:int
    has_next: bool
    has_previous: bool
    page: int
