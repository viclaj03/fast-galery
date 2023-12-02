from sqlalchemy import Column, Table, and_,or_,not_,ForeignKey,DateTime,update
from sqlalchemy.sql.sqltypes import Integer, String,Boolean
from database.connection import meta_data, engine, Base
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.orm import Session
from schemas.user_schema import UserCreate
from database.table import favorite_posts,follow_artist_table
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




def updatae_user_profile(db: Session, user:User,new_email:str,new_name:str,new_password:str = ""):
    

    if new_password != "":
        new_date = update(User).where(User.id == user.id).values(email= new_email,name = new_name,password = new_password)
    else:
        new_date = update(User).where(User.id == user.id).values(email= new_email,name = new_name)
       
    db.execute(new_date)
    db.commit()
    return get_user(db=db,user_id=user.id)


    


def change_user_nsfw_status(db: Session, user:User):
    db.execute(update(User).where(User.id == user.id).values(Nsfw= not user.Nsfw))
    db.commit()
    return not user.Nsfw


def add_follow_artist(db:Session,id_followed_user:User,id_user:int):
    user = db.query(User).filter(User.id == id_user).first()
    followed_user = db.query(User).filter(User.id == id_followed_user).first()
    # Verificar si la publicación ya está en las favoritas del usuario

    if user.id == followed_user.id:
        return {"status":"fail","message":"Que trite es seguirte a uno mismo","actual_value":False}
    
    if followed_user in user.following:
        # Si ya está en las favoritas, la eliminamos 
        user.following.remove(followed_user)
        db.commit()
        return {"status": "success", "message": f"User {followed_user.id} removed from favorites for user {user.id}","actual_value":False}
    else:
        user.following.append(followed_user)
        db.commit()     
    return {"status": "success", "message": f"User {followed_user.id} added to favorites for user {user.id}","actual_value":True}




def get_follow_users(db: Session, user: User, page: int = 1, per_page: int = 2):
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    # Crear una consulta para obtener la lista de usuarios que sigue el usuario actual
    query = db.query(User).join(follow_artist_table, user.id == follow_artist_table.c.follower_id)

    # Filtrar la lista para obtener solo los usuarios que sigue el usuario actual
    following_users = query.filter(follow_artist_table.c.followed_id == User.id).offset(start_index).limit(per_page).all()

    return following_users





    

