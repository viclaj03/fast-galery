from fastapi import APIRouter,Depends,Form,HTTPException,status,File, UploadFile
from database.connection import conn, SessionLocal, engine
from typing import Annotated
from schemas.post_schema import  PostShow,PostBase
from schemas.user_schema import  UserShow
from models.post import add_to_favorite,get_posts,save_new_post,get_post,delete_post_by_id,save_update_post,search_by_tags,get_my_favorites,get_post_by_user
from routers.users_routers import current_user,current_user_optional
from pathlib import Path
import os
from typing import Optional
import uuid
from PIL import Image


UPLOAD_DIR = Path() / 'static/images'
UPLOAD_DIR_RENDER = Path() / 'static/images_render'

router = APIRouter(prefix="/image", 
                   tags=["image"],
                   responses={404:{"message":"post no encontrado"}})














@router.get("/",response_model=list[PostShow])
async def list_posts(user: Optional[UserShow] =  Depends(current_user_optional),page: Optional[int] = 1):
    try:
        if user:
            list_posts = get_posts(SessionLocal(),user,page=page)
        else:
            list_posts = get_posts(SessionLocal(),page=page)
        print(list_posts)
        
        return list_posts
    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}"
    


@router.get("/search",response_model=list[PostShow])
async def search_by_posts_tags(user: UserShow = Depends(current_user_optional),page: Optional[int] = 1,tags: Optional[str] = "" ):
    
    try:
        
        return search_by_tags(db=SessionLocal(),tags=tags,page=page,user=user)     
        
    except Exception as e:
        print(f"Error: {e}") 
        return {"status": "error", "message": str(e)}





@router.get("/image/{id}",response_model=PostShow)
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


#buscar libreria reducir tamaño imagne 2 versiones
@router.post("/",response_model=PostShow)
async def new_post(title:str = Form(...),description:str = Form(...),NSFW:bool = Form(...) , file: UploadFile = File(...),tags:str = Form(...),user: UserShow = Depends(current_user)  ):
    try: 
        
        data_post = PostBase(title=title,description=description,NSFW=NSFW,tags=tags)
        #evita que se repita la imagen y borre las que ya estan
        unique_filename = f"{str(uuid.uuid4())}.{file.filename.split('.')[-1]}"
        save_to = UPLOAD_DIR / unique_filename
        data = await file.read()
        with open(save_to,'wb')as f:
            f.write(data)
        print(data_post.model_dump,user.id)
        #creamos una imagen renderizada mas ligera
        resized_image = Image.open(save_to)
        resized_image.thumbnail((300, 300))  # Ajusta el tamaño según tus necesidades
        resized_filename = f"{str(uuid.uuid4())}_resized.{file.filename.split('.')[-1]}"
        resized_save_to = UPLOAD_DIR_RENDER / resized_filename
        resized_image.save(resized_save_to)
        
        return  save_new_post(db=SessionLocal(),new_image=data_post.model_dump(),image_name=unique_filename,user_auth=user,image_name_ligere=resized_filename)
    
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
        image_ligere = UPLOAD_DIR_RENDER / post.image_url_ligere
        if image_ligere.is_file():
            image_ligere.unlink()
        delete_post_by_id(SessionLocal(),id)
        
        return image       
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}
    


    


@router.put("/posts/{id}")
async def update_post(id:int, title:str = Form(min_length=5,max_length=449),description:str = Form(max_length=500),NSFW:bool = Form(...) ,tags:str = Form(...) ,user: UserShow = Depends(current_user)):
    try:
        post = get_post(SessionLocal(),id)
        post.title = title
        post.description = description
        post.NSFW = NSFW
        post.tags = tags
        if not post:
            raise HTTPException(status.HTTP_404_NOT_FOUND,detail="No existe el post")
        if post.user_id != user.id:
            raise  HTTPException(status.HTTP_403_FORBIDDEN,detail="Usuario no autorizado")
        return save_update_post(SessionLocal(),post)
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}
    

@router.get("/user_post/{id}",response_model=list[PostShow])
async def get_post_from_user(id:int,user: Optional[UserShow] =  Depends(current_user_optional),page: Optional[int] = 1):
    try:
        if user:
            list_posts = get_post_by_user(db=SessionLocal(),user=user,user_id=id,page=page)
        else:
            list_posts = get_post_by_user(db=SessionLocal(),page=page,user_id=id)
        print(list_posts)
        
        return list_posts
    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}" 






    


@router.get("/get_favorites",response_model=list[PostShow])
async def get_favorites(user: UserShow = Depends(current_user)  ):
    return get_my_favorites(db=SessionLocal(),user=user)      

    


@router.post("/add-favorite/{id}")
async def add_post_favorite(id:int, user: UserShow = Depends(current_user)  ):
    try:
        post = get_post(SessionLocal(),id)
        return add_to_favorite(SessionLocal(),post.id,user.id)       
    except Exception as e:
        print(f"Error: {e}") 
    return {"status": "error", "message": str(e)}
    




    



    
