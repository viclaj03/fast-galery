from typing import Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    #id: Optional[int]
    name: str
    #email: str
    
    

class UserCreate(UserBase):
    password: str
    email:str

class UserCount(BaseModel):
    total: int

class UserShow(UserBase):
    id:int
    is_active:bool


class UserProfile(UserShow):
    post_count:int
    follower_count:int
    like_counts:int
    subscribe:bool = False


class UserMe(UserShow):
    email:str
    Nsfw:bool 