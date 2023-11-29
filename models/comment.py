from sqlalchemy import Column,ForeignKey,Table,and_,or_,not_,func,update,desc
from sqlalchemy.sql.sqltypes import Integer, String,DateTime,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session,Mapped
from database.connection import meta_data, engine, Base
from datetime import datetime
from pathlib import Path
from database.table import favorite_posts
from typing import List,Optional



class Coment(Base):
    __tablename__ = "coments"
    #__table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    post_id:Integer = Column(Integer, ForeignKey('posts.id')) 
    user_id:Integer = Column(Integer, ForeignKey('users.id')) 
    content = Column(String(255),nullable=False)
    created_at:DateTime = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='coments')
    #posts = relationship("Post", back_populates='coments',cascade="all,delete")

def get_coment(db:Session,id:int):
    return db.query(Coment).filter(Coment.id == id).first()

def get_coments_by_id_post(db:Session, id:int,page:int, per_page: int = 8):
    start_index = (page - 1) * per_page
    
    coment_query = db.query(Coment).filter(Coment.post_id == id).offset(start_index).limit(per_page).all()
    return  coment_query


def add_coment_to_post(db:Session, id_post:int,content:str,user_id:int):
        

    db_coment = Coment(post_id=id_post,
                     user_id=user_id,
                     content=content)
    db.add(db_coment)
    db.commit()
    db.refresh(db_coment)
    return  db_coment


def delete_comet_post(db:Session, id_coment:int):
    db_coment = db.query(Coment).filter(Coment.id ==id_coment).first()
    db.delete(db_coment)
    db.commit()
    return {'status':"ok"}

    







    
    