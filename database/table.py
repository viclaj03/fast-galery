from sqlalchemy import Column,ForeignKey,Table
from sqlalchemy.sql.sqltypes import Integer, String,DateTime,Boolean,BIGINT

from database.connection import meta_data, engine, Base
from datetime import datetime




Table(
    "users",meta_data, 
    Column("id",Integer, primary_key=True,index=True),
    Column("name",String(255), nullable=False,unique=True),
    Column("email",String(255),nullable=False,unique=True),
    Column("password",String(255),nullable=False),
    Column("NSFW",Boolean,default=False),
    Column("recovery_code",String(255), nullable=True),
    Column("recovery_code_expiration",DateTime, nullable=True),
    Column("is_active",Boolean,default=True),
    Column("created_at",DateTime(),default=datetime.utcnow,nullable=False),  
    )


Table( 
    "messages",meta_data, 
    Column("id",Integer, primary_key=True,index=True),
    Column("title",String(255),nullable=False),
    Column("sender_id",Integer, ForeignKey('users.id',ondelete="CASCADE"),nullable=False),
    Column("receiver_id",Integer, ForeignKey('users.id',ondelete="CASCADE"),nullable=False),
    Column("deleteBySender",Boolean,default=False,nullable=False),
    Column("deleteByReceiver",Boolean,default=False,nullable=False),
    Column("reed",Boolean,default=False,nullable=False),
    Column("content",String(800),nullable=False), 
    Column("created_at",DateTime(),default=datetime.utcnow,nullable=False),  
    )
 


Table(   
    "posts",meta_data,
    Column("id",Integer, primary_key=True,index=True),
    Column("title",String(255), nullable=False),
    Column("description",String(500),nullable=False), 
    Column("image_url",String(255),nullable=False),
    Column("image_url_ligere",String(255),nullable=False),
    Column("tags",String(500),default=" "),

    Column('size',Integer,nullable=False),
    Column('extension',String(255),nullable=False),
    Column('hash_md5',String(255),nullable=False),
    Column("NSFW",Boolean,default=False), 

    Column("user_id",Integer, ForeignKey('users.id',ondelete="CASCADE"),nullable=False),  
    Column("created_at",DateTime(),nullable=False),
    Column("updated_at",DateTime(),nullable=False),
    ) 



Table( 
    "coments",meta_data,
    Column("id",Integer, primary_key=True,index=True),
    Column("user_id",Integer, ForeignKey('users.id',ondelete="CASCADE"),nullable=False),
    Column("post_id",Integer, ForeignKey('posts.id',ondelete="CASCADE"),nullable=False),  
    Column("content",String(500),nullable=False), 
    Column("created_at",DateTime(),nullable=False), 
    )



Table( 
    "reported_posts",meta_data,
    Column("id",Integer, primary_key=True,index=True),
    Column("user_id",Integer, ForeignKey('users.id',ondelete="CASCADE"),nullable=False),
    Column("post_id",Integer, ForeignKey('posts.id',ondelete="CASCADE"),nullable=False),  
    Column("content",String(500),nullable=False), 
    Column("created_at",DateTime(),default=datetime.utcnow,nullable=False), 
)





favorite_posts = Table(
    "favorite_posts",Base.metadata,#para la relacion
    
    Column("post_id", Integer, ForeignKey("posts.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("created_at",DateTime, default=datetime.utcnow),   
)

favorite_posts_table = Table(
    "favorite_posts",meta_data, #para crear la base de datos
    
    Column("post_id", Integer, ForeignKey("posts.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("created_at",DateTime, default=datetime.utcnow),  
)



follow_artist_table = Table(
    "follow_artist",meta_data, #para crear la base de datos
    
    Column("follower_id", Integer, ForeignKey("users.id")),
    Column("followed_id", Integer, ForeignKey("users.id")),  
) 

'''
favorite_artist = Table(
    "follow_artist",Base.metadata,#para la relacion
    
    Column("follower_id", Integer, ForeignKey("users.id")),
    Column("followed_id", Integer, ForeignKey("users.id")),
  
)
'''

  
meta_data.create_all(engine)