from sqlalchemy import Column, Table, and_,or_,not_,ForeignKey,DateTime
from sqlalchemy.sql.sqltypes import Integer, String,Boolean
from database.connection import meta_data, engine, Base
from sqlalchemy.orm import relationship, Mapped,Session
from models.user import User
from schemas.user_schema import UserCreate
from database.table import favorite_posts
from typing import List











def get_user(db:Session,user_id:int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_name_or_email(db:Session,name:String,email=""):
    if email == "":
        email = name
    return db.query(User).filter(or_(User.name==name,User.email == email)).first()

def get_users(db:Session):
    user_query = db.query(User).all()
    return user_query

def delete_user(db:Session,id:int):
    user_query = db.query(User).filter(User.id ==id).first()
    db.delete(user_query)
    db.commit()
    return user_query



def create_user(db: Session, user:UserCreate):
    db_user = User(name=user.name,email=user.email,password = user.password,is_active = True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user





    

