from sqlalchemy import Column,ForeignKey,Table,and_,or_,not_,func,update,desc,case
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
 
#meta_data.create_all(engine)



class Post(Base): 
    __tablename__ = 'posts'
    id: Integer = Column(Integer, primary_key=True,index=True)
    title:String = Column(String(255),nullable=False,)
    description:String = Column(String(500),nullable=False)
    image_url:String = Column(String(255),nullable=False)
    image_url_ligere:String = Column(String(255),nullable=False)
    NSFW:bool = Column(Boolean)
    tags:str = Column(String)
    created_at:DateTime = Column(DateTime, default=datetime.utcnow)
    updated_at:DateTime = Column(DateTime, onupdate=datetime.utcnow)
    user_id:Integer = Column(Integer, ForeignKey('users.id')) 
    favorited_by:Mapped[List[User]] = relationship( "User",secondary=favorite_posts, back_populates="favorite_posts_user")
    # Definir la relación con usuarios
    user = relationship('User', back_populates='posts')  
  




def get_posts(db:Session,user:Optional[User] = None,page: int = 1, per_page: int = 8):
    # Calcular el índice de inicio y fin para la paginación
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    
    if user is not None and user.Nsfw: 
        post_query = db.query(Post).offset(start_index).limit(per_page).all()
    else:
        post_query = db.query(Post).filter(Post.NSFW == False).offset(start_index).limit(per_page).all()


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
    #db.close()
     
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
        return {"status": "success", "message": f"Post {post.id} removed from favorites for user {user.id}","actual_value":False}
    else:
        user.favorite_posts_user.append(post)
        
        db.commit()     
    return {"status": "success", "message": f"Post {post.id} added to favorites for user {user.id}","actual_value":True}


def  save_new_post(db:Session,new_image:PostBase,user_auth:UserShow,image_name:str,image_name_ligere):
     
    
    db_post = Post(title=new_image['title'],
                   description=new_image['description'],
                   image_url = image_name,
                   NSFW = new_image['NSFW'],
                   tags = new_image['tags'],
                   created_at= datetime.now(),
                   updated_at = datetime.now(),
                   user_id = user_auth.id, 
                   image_url_ligere = image_name_ligere)
    print(db.add(db_post))
    db.commit()
    db.refresh(db_post)
    return db_post

def save_update_post(db:Session,image_update:Post):
    
    
    
    db.execute(update(Post).where(Post.id == image_update.id ).values(
        NSFW=  image_update.NSFW,
        title= image_update.title,
        description = image_update.description,
        tags=image_update.tags))
    db.commit()

    return image_update 




#busca por usuario etiquetas y titulo
def search_posts(db:Session,user:Optional[User] = None,tags:str = "",page: int = 1, per_page: int = 8):
    
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    
    
    tag_list = [tag.strip() for tag in tags.split(',')]

    
    base_query = db.query(Post).join(User)

    
    if user is not None and not user.Nsfw:
        base_query = base_query.filter(Post.NSFW == False)
    

    
    user_conditions = [func.lower(User.name).contains(tag.lower()) for tag in tag_list]
    title_conditions = [func.lower(Post.title).contains(tag.lower()) for tag in tag_list]
    tag_conditions = [func.lower(Post.tags).contains(tag.lower()) for tag in tag_list]
    base_query = base_query.filter(or_(*user_conditions,*title_conditions,*tag_conditions))

    # Configurar la cláusula order_by para dar prioridad a los artistas
    base_query = base_query.order_by(
    case(
        (User.name == tags, 0),
        else_=1
    ),
    desc(Post.created_at)  
)

    



    post_query = base_query.offset(start_index).limit(per_page).all()
    
    
    # Actualizar favoritos del usuario
    if post_query and user is not None:
        for post in post_query:
            user_has_favorite = db.query(favorite_posts).filter(
                favorite_posts.c.post_id == post.id,
                favorite_posts.c.user_id == user.id
            ).first()
            post.favorited_by_user = user_has_favorite is not None
            
    return post_query 



async def get_my_favorites(db:Session,user:User,page: int = 1, per_page: int = 8):
    # Calcular el índice de inicio y fin para la paginación
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    try:
        favorite_posts_lists = (
            db.query(Post)
            .join(favorite_posts)  
            .filter(favorite_posts.c.user_id == user.id)  
            .order_by(desc(favorite_posts.c.created_at))
            .offset(start_index)
            .limit(per_page)
            .all()
        )
    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}"

    #db.close()
    return favorite_posts_lists


def get_post_by_user(db:Session,user_id:int,page: int = 1, per_page: int = 8,user:Optional[User] = None):


    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    if user is not None and user.Nsfw: 
        post_query = db.query(Post).filter(Post.user_id==user_id).offset(start_index).limit(per_page).all()
    else:
        post_query = db.query(Post).filter(Post.NSFW == False,Post.user_id==user_id).offset(start_index).limit(per_page).all()


    if post_query:
        if user is not None:
            for post  in post_query:  
                user_has_favorite = db.query(favorite_posts).filter( 
                    favorite_posts.c.post_id == post.id,
                    favorite_posts.c.user_id == user.id
                    ).first() 
                post.favorited_by_user  = user_has_favorite is not None 

 
    return post_query


def get_my_posts_query(db:Session,user_id:int,page: int = 1, per_page: int = 8):

    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    post_query = db.query(Post).filter(Post.user_id==user_id).order_by(desc(Post.created_at)).offset(start_index).limit(per_page).all()

    if post_query:
        
        for post  in post_query:  
            user_has_favorite = db.query(favorite_posts).filter( 
                favorite_posts.c.post_id == post.id,
                favorite_posts.c.user_id == user_id
                ).first() 
            post.favorited_by_user  = user_has_favorite is not None

    return post_query


def get_following_user_posts(db:Session,user:User,page: int = 1, per_page: int = 8):
    user =  db.query(User).filter(User.id == user.id).first()
    
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    #obtenemos los id de los usuarios
    following_user_ids = [followed_user.id for followed_user in user.following]
    if user.Nsfw: 
        post_query = db.query(Post).join(User).filter(User.id.in_(following_user_ids)).order_by(desc(Post.created_at))
    else:
        post_query = db.query(Post).join(User).filter(and_(User.id.in_(following_user_ids),Post.NSFW == False)).order_by(desc(Post.created_at))

    
    
    return post_query.offset(start_index).limit(per_page).all()  


    



