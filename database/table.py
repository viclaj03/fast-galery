from sqlalchemy import Column,ForeignKey,Table
from sqlalchemy.sql.sqltypes import Integer, String,DateTime,Boolean

from database.connection import meta_data, engine, Base




Table(
    "users",meta_data, 
    Column("id",Integer, primary_key=True,index=True),
    Column("name",String(255), nullable=False,unique=True),
    Column("email",String(255),nullable=False,unique=True),
    Column("password",String(255),nullable=False),
    Column("NSFW",Boolean,default=False),
    Column("is_active",Boolean,default=True), 
    )


meta_data.create_all(engine)



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

favorite_posts = Table(
    "favorite_posts",Base.metadata,#meta_data para crear la base de datos
    
    Column("post_id", Integer, ForeignKey("posts.id")),
    Column("user_id", Integer, ForeignKey("users.id")),  
) 

 
meta_data.create_all(engine)