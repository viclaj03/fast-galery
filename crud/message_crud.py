from sqlalchemy import Column,ForeignKey,Table,and_,or_,not_,func,update,desc
from sqlalchemy.sql.sqltypes import Integer, String,DateTime,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session,Mapped
from database.connection import meta_data, engine, Base
from datetime import datetime
from pathlib import Path
from database.table import favorite_posts
from models.messages import Message
from typing import List,Optional
from fastapi import HTTPException





def get_message(db: Session, id: int,user_id:int):
    message = db.query(Message).filter(Message.id == id).first()

    if message.sender_id != user_id and message.receiver_id != user_id:
        return None
    
    message.reed = True
    db.execute(update(Message).where(Message.id == message.id ).values(
        reed=  True,
    ))
    db.commit()

    # Refresca la instancia después de la actualización
    db.refresh(message)
   
    return message





def new_message(db:Session, sender_id:int,receiver_id:int,title:str,content:str):


    db_message = Message(title=title,sender_id=sender_id,receiver_id= receiver_id,content=content,created_at=datetime.now())

    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_reciber_message(db:Session, id:int,page: int = 1, per_page: int = 8):
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    messages = db.query(Message).filter(Message.receiver_id ==id).order_by(desc(Message.id)).offset(start_index).limit(per_page).all()
   
    total_messages = db.query(Message).filter(Message.receiver_id == id).count()

    has_next = end_index < total_messages
    has_previous = start_index > 0


    print(f"messages {messages},total_messages {total_messages},has_next: {has_next},has_previous: {has_previous},page: {page},")
    
    return {
        "messages": messages,
        "total_messages": total_messages, 
        "has_next": has_next, 
        "has_previous": has_previous,
        "page": page,

    }




def get_sender_message(db:Session, id:int,page: int = 1, per_page: int = 8):
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    messages = db.query(Message).filter(Message.sender_id ==id).offset(start_index).limit(per_page).all()
   
    total_messages = db.query(Message).filter(Message.sender_id == id).count()

    has_next = end_index < total_messages
    has_previous = start_index > 0

    return {
        "messages": messages,
        "total_messages": total_messages,
        "has_next": has_next,
        "has_previous": has_previous,
        "page": page,

    }

