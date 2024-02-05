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


    message = get_message(db= SessionLocal(),id=id,user_id=user.id)
    if message == None:
        raise  HTTPException(status.HTTP_403_FORBIDDEN,detail="Usuario no autorizado")  
    
    

    return message



@router.post("/send-message",response_model=MessageShow)
async def image(user: UserShow =  Depends(current_user), title:str = Form(...),content:str = Form(...),receiver_id:int = Form(...)):


    return new_message(db=SessionLocal(),sender_id=user.id,title=title,content=content,receiver_id=receiver_id)


@router.get("/get-messages-reciver",response_model=MessageList)
async def image(user: UserShow =  Depends(current_user),page: Optional[int] = 1 ):

    try:
        return get_reciber_message(db=SessionLocal(),id=user.id,page=page)
    except Exception as e:
        print(f"Error: {e}")
        return []

@router.get("/get-messages-sender",response_model=MessageList)
async def image(user: UserShow =  Depends(current_user),page: Optional[int] = 1 ):
    try:
        messages = get_sender_message(db=SessionLocal(),id=user.id,page=page)
        return messages #JSONResponse(content=messages)
    except Exception as e:
        print(f"Error: {e}")
        return []
    

@router.delete("/message/{id}")
async def image(id:int,user: UserShow =  Depends(current_user)):


    message = delete_message(db= SessionLocal(),id=id,user_id=user.id)
    if message == None:
        raise  HTTPException(status.HTTP_403_FORBIDDEN,detail="Usuario no autorizado")  
    
    

    return message
    
