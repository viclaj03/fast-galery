from pydantic import BaseModel
from datetime import datetime
from schemas.user_schema import UserShow


class ComentBase(BaseModel):
    post_id:int
    content:str
    created_at:datetime





class ComentShow(ComentBase):
    id:int
    user:UserShow