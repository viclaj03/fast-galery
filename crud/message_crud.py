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


#Aqui gestionamos el CRUD de los mensajes

#obtines un mensaje selecionado
def get_message(db: Session, id: int,user_id:int):
    message = db.query(Message).filter(Message.id == id).first()
    #comprobamos que el que quiere ver el mensaje es el que mando mensaje o el que lo recibe
    if message.sender_id != user_id and message.receiver_id != user_id:
        return None
    
    if message.sender_id == user_id and message.deleteBySender == True:
        return None
    
    if message.receiver_id == user_id and message.deleteByReceiver == True:
        return None

    #si es el que lo recibe cambiamos su estado a leido 
    if message.receiver_id == user_id:   
        db.execute(update(Message).where(Message.id == message.id ).values(reed=  True,))
        db.commit()
        db.refresh(message)
   
    return message

'''
aqui "borramos" los mensajes.
En relidad lo que hacemos es cambiar un valor en la base de datos
lo que hacemos es cambiar a true una columna que hace referencia
de si lo ha eliminado el que envia o el que recibe el mensaje
la idea es que el que lo reciba pueda borrar el mensaje si que con ello
lleve a que el que lo envio pierda el mensaje y viceversa,
el otro motivo es si el mansaje tiene contenido inapropiado se pueda revisar
sin riesgo a que el que lo mado lo borre y elimine pruebas
'''
def delete_message(db: Session, id: int,user_id:int):
    message = db.query(Message).filter(Message.id == id).first()
    #comprobamos que el usuario tiene permitido esta acción
    if message.sender_id != user_id and message.receiver_id != user_id:
        return None
    #cambiamos el estado de la columna a true si es el recibidor
    if message.receiver_id == user_id:
        db.execute(update(Message).where(Message.id == message.id ).values(deleteByReceiver =  True,))
        db.commit()
    
    #cambiamos el estado de la columna a true si es el que lo a enviado
    if message.sender_id == user_id:
        db.execute(update(Message).where(Message.id == message.id ).values(deleteBySender =  True,))
        db.commit()

        
    return {'status':"ok"}




#creamos un mensaje
def new_message(db:Session, sender_id:int,receiver_id:int,title:str,content:str):

    db_message = Message(title=title,sender_id=sender_id,receiver_id= receiver_id,content=content,created_at=datetime.now())

    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


#obtenemos los mensajes que hemos recibidos
def get_reciber_message(db:Session, id:int,page: int = 1, per_page: int = 8):
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    messages = db.query(Message).filter(and_(Message.receiver_id ==id,Message.deleteByReceiver == False)).order_by(desc(Message.id)).offset(start_index).limit(per_page).all()
   
   #obtenemos el numero total de mensajes
    total_messages = db.query(Message).filter(and_(Message.receiver_id ==id,Message.deleteByReceiver == False)).count()

    has_next = end_index < total_messages
    has_previous = start_index > 0


    print(f"messages {messages},total_messages {total_messages},has_next: {has_next},has_previous: {has_previous},page: {page},")
    
    #en este caso aparte de devolver el mensaje tan bien devolvemos unos valores que nos ayudan a paginar
    return {
        "messages": messages,
        "total_messages": total_messages, 
        "has_next": has_next, 
        "has_previous": has_previous,
        "page": page,

    }



#obtenemos los mensajes que hemos recibidos
def get_sender_message(db:Session, id:int,page: int = 1, per_page: int = 8):
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    messages = db.query(Message).filter(and_(Message.sender_id ==id,Message.deleteBySender == False)).order_by(desc(Message.id)).offset(start_index).limit(per_page).all()
   
    total_messages = db.query(Message).filter(and_(Message.sender_id ==id,Message.deleteBySender == False)).count()

    has_next = end_index < total_messages
    has_previous = start_index > 0

    return {
        "messages": messages,
        "total_messages": total_messages,
        "has_next": has_next,
        "has_previous": has_previous,
        "page": page,

    }

