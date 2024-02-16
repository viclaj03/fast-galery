from sqlalchemy import Column,ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String,DateTime,Boolean
from sqlalchemy.orm import relationship
from database.connection import  Base
from datetime import datetime









class Message(Base): 
    __tablename__ = 'messages'
    id: Integer = Column(Integer, primary_key=True,index=True)
    title:String = Column(String(255),nullable=False,)
    content:String = Column(String(800),nullable=False)
    sender_id:Integer = Column(Integer, ForeignKey('users.id')) 
    receiver_id:Integer = Column(Integer, ForeignKey('users.id')) 
    created_at:DateTime = Column(DateTime, default=datetime.utcnow)
    reed:bool = Column(Boolean,default=False)
    deleteBySender:bool = Column(Boolean,default=False)
    deleteByReceiver:bool = Column(Boolean,default=False)
    user_sender = relationship('User', 
                               back_populates='message_sender',
                               foreign_keys=[sender_id])
    user_reciber = relationship('User',
                                back_populates='message_reciber',
                                foreign_keys=[receiver_id])
    