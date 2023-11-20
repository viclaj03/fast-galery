from fastapi import APIRouter,Depends,Form,HTTPException,status,File, UploadFile
from database.connection import conn, SessionLocal, engine
from typing import Annotated
from schemas.post_schema import  PostShow,PostBase
from schemas.user_schema import  UserShow
from models.post import add_to_favorite,get_posts,save_new_post,get_post,delete_post_by_id
from routers.users_routers import current_user,current_user_optional
from pathlib import Path
import os
from typing import Optional


UPLOAD_DIR = Path() / 'static/images'

router = APIRouter(prefix="/image", 
                   tags=["image"],
                   responses={404:{"message":"post no encontrado"}})






@router.get("/",response_model=list[PostShow])
async def images(user: Optional[UserShow] =  Depends(current_user_optional)):
    try:
        if user:
            list_posts = get_posts(SessionLocal(),user)
        else:
            list_posts = get_posts(SessionLocal())
        print(list_posts)
        
        return list_posts
    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}"


@router.get("/{id}",response_model=PostShow)
async def image(id:int,user: Optional[UserShow] =  Depends(current_user_optional)):
    try:
        if user:
            post = get_post(db= SessionLocal(),id=id,user_id=user.id)
        else:
            post = get_post(db= SessionLocal(),id=id)
        
        if not post:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        return post
    except Exception as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND)      



@router.post("/")
async def new_post(title:str = Form(...),description:str = Form(...),NSFW:bool = Form(...) , file: UploadFile = File(...),user: UserShow = Depends(current_user)  ):
    try: 
        
        data_post = PostBase(title=title,description=description,NSFW=NSFW)
        save_to = UPLOAD_DIR /file.filename
        data = await file.read()
        with open(save_to,'wb')as f:
            f.write(data)
        print(data_post.model_dump,user.id)
        
        return await save_new_post(db=SessionLocal(),new_image=data_post.model_dump(),image_name=file.filename,user_auth=user)
    
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}   
    

@router.delete("/{id}")
async def delete_post(id:int, user: UserShow = Depends(current_user)  ):
    try:
        post = get_post(SessionLocal(),id)
        
        if not post:
            raise HTTPException(status.HTTP_404_NOT_FOUND,detail="No existe el post")

        if post.user_id != user.id:
            raise  HTTPException(status.HTTP_403_FORBIDDEN,detail="Usuario no autorizado")
        image = UPLOAD_DIR / post.image_url
        if image.is_file():
            image.unlink()
        delete_post_by_id(SessionLocal(),id)
        #os.remove(UPLOAD_DIR)
        return image       
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}
    

@router.post("/add-favorite-{id}")
async def add_post_favorite(id:int, user: UserShow = Depends(current_user)  ):
    try:
        post = get_post(SessionLocal(),id)
        return add_to_favorite(SessionLocal(),post.id,user.id)       
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}

    
