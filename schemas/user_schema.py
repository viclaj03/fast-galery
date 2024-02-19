from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    password: str
    email:str

class UserCount(BaseModel):
    total: int

class UserShow(UserBase):
    id:int
    is_active:bool
    created_at:datetime


class UserProfile(UserShow):
    post_count:int
    follower_count:int
    like_counts:int
    subscribe:bool = False
    email:Optional[str] = None


class UserMe(UserShow):
    email:str
    Nsfw:bool 