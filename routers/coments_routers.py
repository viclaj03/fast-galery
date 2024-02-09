from fastapi import APIRouter,Depends,Form,HTTPException,status,File, UploadFile
from database.connection import conn, SessionLocal, engine
from routers.users_routers import current_user
from schemas.coment_schema import ComentShow
from schemas.user_schema import UserShow
from crud.comment_crud import *
from models.post import get_post

from typing import Optional


 
 


router = APIRouter(prefix="/comments", 
                   tags=["comment"],
                   responses={404:{"message":"coment no encontrado"}})









@router.get("/{id}",response_model=list[ComentShow]  )
async def get_coments_by_post(id:int,page: Optional[int] = 1):
    return get_coments_by_id_post(db=SessionLocal(),id=id,page=page)
   



@router.post("",response_model=ComentShow)
async def new_coment(content:str = Form(...),user: UserShow = Depends(current_user),id_post:int=Form(...)  ):
    
    if not get_post(db=SessionLocal(),id=id_post):
        raise HTTPException(status.HTTP_404_NOT_FOUND,detail="No existe el post")

    try: 
        return add_coment_to_post(db=SessionLocal(),content=content,id_post=id_post,user_id=user.id)
    except Exception as e:
        print(f"Error: {e}")
    return {"status": "error", "message": str(e)}   
    


@router.delete("/{id}")
async def delete_coment(id:int, user: UserShow = Depends(current_user)  ):
    coment = get_coment(SessionLocal(),id)  

    if not coment:
        raise HTTPException(status.HTTP_404_NOT_FOUND,detail="No existe el comentario")

    if coment.user_id != user.id:
        raise  HTTPException(status.HTTP_403_FORBIDDEN,detail="Usuario no autorizado")
    try:
        return  delete_comet_post(db=SessionLocal(),id_coment=id)   
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}
    


    

    



    
