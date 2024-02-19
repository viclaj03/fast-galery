from sqlalchemy import Column,ForeignKey,Table,and_,or_,not_,func,update,desc
from sqlalchemy.sql.sqltypes import Integer, String,DateTime,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session,Mapped
from database.connection import meta_data, engine, Base
from datetime import datetime
from pathlib import Path
from database.table import favorite_posts
from typing import List,Optional




class Report(Base):
    __tablename__ = "reported_posts"
    id = Column(Integer, primary_key=True, index=True)
    post_id:Integer = Column(Integer, ForeignKey('posts.id')) 
    user_id:Integer = Column(Integer, ForeignKey('users.id')) 
    content = Column(String(255),nullable=False)
    created_at:DateTime = Column(DateTime, default=datetime.utcnow) 

 








    