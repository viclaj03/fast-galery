from sqlalchemy import Column,ForeignKey,Table
from sqlalchemy.sql.sqltypes import Integer, String,DateTime,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session,Mapped
from database.connection import meta_data, engine, Base
from datetime import datetime
from models.user import User
from schemas.user_schema import UserShow
from schemas.post_schema import PostBase,PostShow
from pathlib import Path
from database.table import favorite_posts
from typing import List,Optional



UPLOAD_DIR = Path() / 'static/images'
#Base = declarative_base()

'''

Table( 
    "posts",meta_data,
    Column("id",Integer, primary_key=True,index=True),
    Column("title",String(255), nullable=False),
    Column("description",String(255),nullable=False), 
    Column("image_url",String(255),nullable=False), 
    Column("created_at",DateTime(),nullable=False),
    Column("updated_at",DateTime(),nullable=False),
    Column("NSFW",Boolean,default=False),     
    Column("user_id",Integer, ForeignKey('users.id',ondelete="CASCADE"),nullable=False), 
 
    )
'''
 
meta_data.create_all(engine)



class Post(Base): 
    __tablename__ = 'posts'
    id: Integer = Column(Integer, primary_key=True,index=True)
    title:String = Column(String(255),nullable=False,)
    description:String = Column(String(255),nullable=False)
    image_url:String = Column(String(255),nullable=False)
    NSFW:bool = Column(Boolean)
    created_at:DateTime = Column(DateTime, default=datetime.utcnow)
    updated_at:DateTime = Column(DateTime, onupdate=datetime.utcnow)
    user_id:Integer = Column(Integer, ForeignKey('users.id')) 
    favorited_by:Mapped[List[User]] = relationship( "User",secondary=favorite_posts, back_populates="favorite_posts_user")
    # Definir la relación con usuarios
    user = relationship('User', back_populates='posts')  
  




def get_posts(db:Session,user:Optional[User] = None):
    if user is not None and user.Nsfw: 
        post_query = db.query(Post).join(User,Post.user_id == User.id).all()
    else:
        post_query = db.query(Post).filter(Post.NSFW == False).all()


    if post_query:
        if user is not None:
            for post  in post_query:  
                user_has_favorite = db.query(favorite_posts).filter(
                    favorite_posts.c.post_id == post.id,
                    favorite_posts.c.user_id == user.id
                ).first() 
                post.favorited_by_user  = user_has_favorite is not None 


    return post_query

def get_post(db:Session, id:int, user_id:Optional[int] = None):
    post_query = db.query(Post).filter(Post.id ==id).join(User,Post.user_id == User.id).first()
    if post_query:
        if user_id is not None:
            user_has_favorite = db.query(favorite_posts).filter(
                favorite_posts.c.post_id == id,
                favorite_posts.c.user_id == user_id
            ).first()
            post_query.favorited_by_user = user_has_favorite is not None

        
    return post_query

def delete_post_by_id(db:Session,id:int):
    post_query = db.query(Post).filter(Post.id ==id).first()
    db.delete(post_query)
    db.commit()
    return post_query

def add_to_favorite(db:Session,id_post:Post,id_user:int):
    user = db.query(User).filter(User.id == id_user).first()
    post = db.query(Post).filter(Post.id == id_post).first()
    # Verificar si la publicación ya está en las favoritas del usuario
    if post in user.favorite_posts_user:
        # Si ya está en las favoritas, la eliminamos f
        user.favorite_posts_user.remove(post)
        db.commit()
        return {"status": "success", "message": f"Post {post.id} removed from favorites for user {user.id}"}
    else:
        user.favorite_posts_user.append(post)
        db.commit() 
    return {"status": "success", "message": f"Post {post.id} added to favorites for user {user.id}"}

async def  save_new_post(db:Session,new_image:PostBase,user_auth:UserShow,image_name:str):
     
    
    db_post = Post(title=new_image['title'],
                   description=new_image['description'],
                   image_url = image_name,
                   NSFW = new_image['NSFW'],
                   created_at= datetime.now(),
                   updated_at = datetime.now(),
                   user_id = user_auth.id)
    print(db.add(db_post))
    db.commit()
    db.refresh(db_post)
    return db_post


