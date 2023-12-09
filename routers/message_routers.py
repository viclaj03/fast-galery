from fastapi import APIRouter,Depends,Form,HTTPException,status,File, UploadFile
from database.connection import conn, SessionLocal, engine
from routers.users_routers import current_user
from schemas.coment_schema import ComentShow
from schemas.user_schema import UserShow
from crud.message_crud import *
from schemas.message_schema import *
from fastapi.responses import JSONResponse





router = APIRouter(
                   tags=["message"],
                   responses={404:{"message":"coment no encontrado"}})






@router.get("/message/{id}",response_model=MessageShow)
async def image(id:int,user: UserShow =  Depends(current_user)):


    message = get_message(db= SessionLocal(),id=id)
    if message.sender_id != user.id and message.receiver_id != user.id:
        raise  HTTPException(status.HTTP_403_FORBIDDEN,detail="Usuario no autorizado")  

    return message



@router.post("/send-message",response_model=MessageShow)
async def image(user: UserShow =  Depends(current_user), title:str = Form(...),content:str = Form(...),receiver_id:int = Form(...)):


    return new_message(db=SessionLocal(),sender_id=user.id,title=title,content=content,receiver_id=receiver_id)


@router.get("/get-messages-reciver",response_model=list[MessageShow])
async def image(user: UserShow =  Depends(current_user),page: Optional[int] = 1 ):


    return get_reciber_message(db=SessionLocal(),id=user.id,page=page)


@router.get("/get-messages-sender",response_model=MessageList)
async def image(user: UserShow =  Depends(current_user),page: Optional[int] = 1 ):

    messages = get_sender_message(db=SessionLocal(),id=user.id,page=page)
    return messages #JSONResponse(content=messages)
