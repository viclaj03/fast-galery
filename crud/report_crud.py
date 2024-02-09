from sqlalchemy import Column,ForeignKey,Table,and_,or_,not_,func,update,desc
from sqlalchemy.sql.sqltypes import Integer, String,DateTime,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session,Mapped
from database.connection import meta_data, engine, Base
from datetime import datetime
from pathlib import Path
from database.table import favorite_posts
from models.report import Report



#reporta un post

def add_report_to_post(db:Session, id_post:int,content:str,user_id:int):
        

    db_coment = Report(post_id=id_post,
                     user_id=user_id,
                     content=content)
    db.add(db_coment)
    db.commit()
    db.refresh(db_coment)
    return  db_coment
