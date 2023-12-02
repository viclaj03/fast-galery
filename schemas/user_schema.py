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


class UserMe(UserShow):
    email:str
    Nsfw:bool