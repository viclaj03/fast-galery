from typing import Optional
from pydantic import BaseModel
from datetime import datetime,timedelta
from schemas.user_schema import UserShow

class PostBase(BaseModel):
    #id: Optional[int]
    title: str
    description: str
    NSFW:bool
    favorited_by_user: bool=False
    



class PostShow(PostBase):
    id:int
    image_url:str
    created_at:datetime
    updated_at:datetime
    user:UserShow

