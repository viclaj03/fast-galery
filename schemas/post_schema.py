from typing import Optional
from pydantic import BaseModel
from datetime import datetime,timedelta
from schemas.user_schema import UserShow

class PostBase(BaseModel):
    #id: Optional[int]
    title: str
    description: str
    NSFW:bool
    tags:str
    size:int
    extension:str
    hash_md5:str
    
    



class PostShow(PostBase):
    id:int
    image_url:str
    image_url_ligere:str
    created_at:datetime
    updated_at:datetime
    favorited_by_user: bool=False
    user:UserShow

