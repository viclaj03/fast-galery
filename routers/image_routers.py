from fastapi import APIRouter,Depends,Form,HTTPException,status,File, UploadFile
from database.connection import conn, SessionLocal, engine
from typing import Annotated
from schemas.post_schema import  PostShow,PostBase
from schemas.user_schema import  UserShow
#from models.post import add_to_favorite,get_posts,save_new_post,get_post,delete_post_by_id,save_update_post,search_posts,get_my_favorites,get_post_by_user,get_my_posts_query,get_following_user_posts 
from crud.post_crud import *
from routers.users_routers import current_user,current_user_optional
from pathlib import Path
import os
from typing import Optional
import uuid
from PIL import Image
import hashlib


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
    
 

@router.get("/search",response_model=list[PostShow],description="Search image, priority for the artists name")
async def search_posts_by_tags_or_title_or_Artist(user: Optional[UserShow] = Depends(current_user_optional),page: Optional[int] = 1,search_content: Optional[str] = "" ):
    
    try: 
        if user:
            return search_posts(db=SessionLocal(),tags=search_content,page=page,user=user)
        else:
            return search_posts(db=SessionLocal(),tags=search_content,page=page) 
        
    except Exception as e:
        print(f"Error: {e}") 
        return {"status": "error", "message": str(e)}





@router.get("/get/{id}",response_model=PostShow)
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
async def new_post(title:str = Form(...),description:str = Form(...),NSFW:bool = Form(...) , tags:str = Form(...),file: UploadFile = File(description="only image file",),user: UserShow = Depends(current_user)  ):
    # Lista de extensiones permitidas
    allowed_extensions = ["jpg", "jpeg", "png", "gif","webp"]
    file_extension = file.filename.split(".")[-1].lower()
    print(file_extension)
    if file_extension not in allowed_extensions:
        
        raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="Only images")
    
       
    try:  

        #obtenmos un hash md5 para verificar que la imagen es unica
        file_content = b""
        
 
        #evita que se repita la imagen y borre las que ya estan
        unique_filename = f"{str(uuid.uuid4())}.{file.filename.split('.')[-1]}"
        extension = f"{file.filename.split('.')[1]}"
        
        save_to = UPLOAD_DIR / unique_filename
        data = await file.read() 
        with open(save_to,'wb')as f:
            size = len(data)
            file_content += data
            f.write(data)
        md5_hash = hashlib.md5(file_content).hexdigest()
            
            
        
        
        
        
        #creamos una imagen renderizada mas ligera
        resized_image = Image.open(save_to)
        
        resized_image.thumbnail((400, 400))   
        resized_filename = f"{str(uuid.uuid4())}_resized.png"
        resized_save_to = UPLOAD_DIR_RENDER / resized_filename 
        resized_image.save(resized_save_to)


        data_post = PostBase(title=title,description=description,NSFW=NSFW,tags=tags, size=size,extension=extension,hash_md5=md5_hash)
        #print(data_post.model_dump,user.id)
        
        
        return  save_new_post(db=SessionLocal(),new_image=data_post.model_dump(),image_name=unique_filename,user_auth=user,image_name_ligere=resized_filename)
    
    except Exception as e:
        #si no se guarda el post eliminamos las fotos 
        
        if save_to.is_file():
            save_to.unlink()
        #if resized_save_to.exists() and resized_save_to.is_file():
        #    resized_save_to.unlink() 
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
        
        return {"status":"succes","message":f"Post {post.title} eliminado"}       
    except Exception as e:
        print(f"Error: {e}") 
        return {"status": "error", "message": str(e)}
     


    


@router.put("/{id}") 
async def update_post(id:int, title:str = Form(min_length=5,max_length=50),description:str = Form(max_length=500),NSFW:bool = Form(...) ,tags:str = Form(...) ,user: UserShow = Depends(current_user)):
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
    

@router.get("/user-post/{id}",response_model=list[PostShow])
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






@router.get("/my-posts",response_model=list[PostShow])  
async def get_my_posts(user = Depends(current_user),page: Optional[int] = 1):
    return get_my_posts_query(db=SessionLocal(),user_id=user.id,page=page)


@router.get("/get-favorites",response_model=list[PostShow])
async def get_favorites(user: UserShow = Depends(current_user), page: Optional[int] = 1):
    try:
        return  get_my_favorites(db=SessionLocal(),user=user,page=page)
    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}" 


@router.get("/get-following-post",response_model=list[PostShow])
async def get_posts_by_folloing(user = Depends(current_user),page:Optional[int]= 1):
    
    return get_following_user_posts(db=SessionLocal(),user=user,page=page)

    


@router.post("/add-favorite/{id}",description='Añade un posts a favoritos',name='Añade un posts a favoritos',)
async def add_post_favorite(id:int, user: UserShow = Depends(current_user)  ): 
    try:
        post = get_post(SessionLocal(),id)
        return add_to_favorite(SessionLocal(),post.id,user.id)       
    except Exception as e:
        print(f"Error: {e}") 
    return {"status": "error", "message": str(e)}
    




    



    
