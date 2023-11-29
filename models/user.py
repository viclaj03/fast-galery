from sqlalchemy import Column, Table, and_,or_,not_,ForeignKey,DateTime,update
from sqlalchemy.sql.sqltypes import Integer, String,Boolean
from database.connection import meta_data, engine, Base
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.orm import Session
from schemas.user_schema import UserCreate
from database.table import favorite_posts
from typing import List






class User(Base):
    __tablename__ = "users"
    #__table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False,unique=True)
    email = Column(String(255), nullable=False,unique=True)
    password = Column(String(255), nullable=False) 
    Nsfw = Column(Boolean,default=False,nullable=False)
    is_active = Column(Boolean,default=True) #nueva columna
    posts = relationship("Post", back_populates='user',cascade="all,delete")
    coments = relationship("Coment",back_populates='user',cascade="all,delete")
    favorite_posts_user = relationship("Post",secondary=favorite_posts, back_populates="favorited_by") 




def get_user(db:Session,user_id:int):
    user_db = db.query(User).filter(User.id == user_id).first()

    return user_db

def get_user_by_name_or_email(db:Session,name:String,email:str=""):
    if email == "":
        email = name
    return db.query(User).filter(or_(User.name==name,User.email == email)).first()



def get_user_by_name(db:Session,name:str):
    
    return db.query(User).filter(User.name==name).first()


def get_user_by_email(db:Session,email:str):
    
    return db.query(User).filter(User.email==email).first()



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




def updtae_user_profile(db: Session, user:User,new_email:str,new_name:str,new_password:str = ""):
    

    if new_password != "":
        new_date = update(User).where(User.id == user.id).values(email= new_email,name = new_name,password = new_password)
    else:
        new_date = update(User).where(User.id == user.id).values(email= new_email,name = new_name)
       
    db.execute(new_date)
    db.commit()
    return get_user(db=db,user_id=user.id)


    
    
    print('bene')

def change_user_nsfw_status(db: Session, user:User):
    db.execute(update(User).where(User.id == user.id).values(Nsfw= not user.Nsfw))
    db.commit()
    return True





    

