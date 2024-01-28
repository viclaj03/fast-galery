from fastapi import APIRouter,Depends,Form,HTTPException,status,File, UploadFile
from database.connection import conn, SessionLocal, engine
from routers.users_routers import current_user
from schemas.user_schema import UserShow
from crud.report_crud import *
from models.post import get_post



from typing import Optional






router = APIRouter(prefix="/report",  
                   tags=["repor"],
                   responses={404:{"message":"coment no encontrado"}})




@router.post("/{id}") 
async def new_report(id:int,content:str = Form(...),user: UserShow = Depends(current_user) ):

    if not get_post(db=SessionLocal(),id=id):
        raise HTTPException(status.HTTP_404_NOT_FOUND,detail="No existe el post")

    
    try:  
        return add_report_to_post(db=SessionLocal(),content=content,id_post=id,user_id=user.id) 
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}
    return {"status": "error", "message": 'Error desconocido'}      