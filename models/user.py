from sqlalchemy import Column, Table, and_,or_,not_,ForeignKey,DateTime,update,select

from sqlalchemy.sql.sqltypes import Integer, String,Boolean
from database.connection import meta_data, engine, Base
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.orm import Session
from schemas.user_schema import UserCreate
from database.table import favorite_posts,follow_artist_table

from datetime import datetime

import time
 
from pathlib import Path
UPLOAD_DIR = Path() / 'static/images'
UPLOAD_DIR_RENDER = Path() / 'static/images_render'






class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False,unique=True)
    email = Column(String(255), nullable=False,unique=True)
    password = Column(String(255), nullable=False) 
    Nsfw = Column(Boolean,default=False,nullable=False)
    created_at:DateTime = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean,default=True) #nueva columna
    recovery_code = Column(String(255), nullable=True)
    recovery_code_expiration = Column(DateTime, nullable=True)
    #relaciones entre tablas
    posts = relationship("Post", back_populates='user',cascade="all,delete")
    coments = relationship("Coment",back_populates='user',cascade="all,delete")
    favorite_posts_user = relationship("Post",secondary=favorite_posts, back_populates="favorited_by")
    #relacion entre usarios seguidores y seguidos
    following = relationship(
        "User",
        secondary=follow_artist_table,
        back_populates="followers",
        primaryjoin=id == follow_artist_table.c.follower_id,
        secondaryjoin=id == follow_artist_table.c.followed_id
    )
    followers = relationship(
        "User",
        secondary=follow_artist_table,
        back_populates="following",
        primaryjoin=id == follow_artist_table.c.followed_id,
        secondaryjoin=id == follow_artist_table.c.follower_id
    )
    message_sender = relationship('Message',
                                  back_populates='user_sender',
                                  foreign_keys='Message.sender_id',
                                  cascade="all,delete")
    message_reciber = relationship('Message',
                                   back_populates='user_reciber',
                                   foreign_keys='Message.receiver_id',
                                   cascade="all,delete")

    def count_posts(self):
        return len(self.posts)
    def count_followes(self):
        return len(self.followers) 
    
    def count_likes(self):
        total_likes = 0
        for post in self.posts:
            total_likes += len(post.favorited_by)
        return total_likes
    








    

