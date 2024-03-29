from fastapi import APIRouter,Depends,HTTPException,status,Form
from pydantic import EmailStr
from database.connection import conn, SessionLocal, engine
from models.user import User
from crud.user_crud import *

from schemas.user_schema import  UserCreate,UserShow,UserMe,UserProfile
from typing import List

from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta
from typing import Optional

from functions.email import *

import secrets

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION_MINUTES = 1
ACCESS_TOKEN_DURATION_HOURS = 12 
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

  


router = APIRouter()

oauth2 = OAuth2PasswordBearer(tokenUrl="login",auto_error=False)



crypt = CryptContext(schemes=["bcrypt"],) 


from cryptography.fernet import Fernet



router = APIRouter(tags=["users"])



#token
async def auth_user(token: str = Depends(oauth2)):
    
    exception = HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Creedenciales inavlidas",
            headers={"WWW-Authenticate":"Bearer"})
    try:
        id = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM]).get("id")
        if id is None:
            print('invailda')
            raise exception
         
    except Exception: 
        print('not id')  
        id = 0
    return  get_user(SessionLocal(),id)   
    
 
 

    
async def current_user(user: UserShow = Depends(auth_user)):
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,detail="Usuario inactivo")
    return user

async def current_user_optional(user: UserShow = Depends(auth_user)):
    
    if not user or not user.is_active:
        return False
    return user

#fin token



@router.get("/users",response_model=list[UserShow])
async def users():  
    
    try:
        list_users = await get_users(SessionLocal())
        print(list_users)
        return list_users
    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}"
    

 

@router.get("/users-search",response_model=list[UserShow])
async def users_search(name:str):  
    
    try:
        list_users = await get_users_search(SessionLocal(),name)
        print(list_users)
        return list_users
    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}"
    
@router.get("/user/{id}",response_model=UserProfile,description="obtener los datos de un usuario")
async def user(id: int,user_me:UserShow = Depends(current_user_optional)): 

    if user_me:
        user =  get_user_profile(SessionLocal(),id,user=user_me)
    else:
        user =  get_user_profile(SessionLocal(),id)       
    if not user:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="el usuario no se encontro") 
    return user


    
    


@router.post("/registre")
async def registre(name:str = Form(max_length=255),
                   email:str = Form(pattern="^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+"),
                   password:str = Form(...)): 
   
    validar_contraseña(password)
    user = UserCreate(name=name,email=email,password=password)

    if get_user_by_name_or_email(SessionLocal(),user.name,user.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="el usuario y/o correo ya ha sido registrado")
    
    try:
        user.password = crypt.hash(user.password)
        print(user)
        new_user = create_user(db= SessionLocal(),user=user)
        access_token ={"sub":new_user.name,
                   "id":new_user.id,
                   "exp":datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION_MINUTES,hours=ACCESS_TOKEN_DURATION_HOURS)}
 

        return {"access_token":jwt.encode(access_token,SECRET_KEY,algorithm=ALGORITHM),"token_type":"bearer","id":new_user.id}

    except Exception as e:
        return f"Error al insertar en la base de datos: {str(e)}"
    

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    
    user_db = get_user_by_name_or_email(SessionLocal(),name = form.username)    
    if not user_db:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="el usuario no se encontro")
    if not crypt.verify(form.password,user_db.password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="la contraseña es incorrecta")

    access_token ={"sub":user_db.name,
                   "id":user_db.id,
                   "exp":datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION_MINUTES,hours=ACCESS_TOKEN_DURATION_HOURS)}


    return {"access_token":jwt.encode(access_token,SECRET_KEY,algorithm=ALGORITHM),"token_type":"bearer"} 

@router.delete("/user")
async def user(user:UserShow = Depends(current_user)): 
    try:
        delete_user(SessionLocal(),user.id)
        return {"ok":"User delete"}
    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}"



@router.get("/users/me",response_model=UserMe)
async def me(user:User = Depends(current_user)):
        return user


@router.post("/user-follow/{id}")
async def follow_artis(id:int,user:User = Depends(current_user)):
    return add_follow_artist(db=SessionLocal(),id_user=user.id,id_followed_user=id)




@router.get("/user-follow",response_model=list[UserShow])
async def get_my_favorite_artists(user:User= Depends(current_user),page: Optional[int] = 1):
    return get_follow_users(db=SessionLocal(),user=user,page=page)


@router.put("/update_profile",response_model=UserMe)
async def updete_my_profile(name:str = Form(max_length=255),email:str= Form(pattern="^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+"),password:Optional[str]=Form(default=""),user:UserShow = Depends(current_user)):
        
        if user.email != email and get_user_by_email(SessionLocal(),email=email):
            raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="email ya en uso")
        if user.name != name and get_user_by_name(SessionLocal(),name=name):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="nombre de usuario en uso")
        
        
        if password != "":
            validar_contraseña(password)
            password = crypt.hash(password)
            
        
        try: 
            return  updatae_user_profile(db=SessionLocal(),new_email=email,new_name=name,new_password=password,user=user)
        except Exception as e:
            HTTPException(status.HTTP_400_BAD_REQUEST,detail=f"Error:{str(e)}")
        

 

@router.patch("/change-nsfw/")
async def update_post(user: UserShow = Depends(current_user)):
    return change_user_nsfw_status(db=SessionLocal(),user=user)


@router.post("/forgot-password",description="Envia un email con una clave para recueperar la contraseña")
async def forgot_password(email: str = Form(pattern="^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+",description="email al que se le enviara el codigo de recuperación")):
    user = get_user_by_email(db=SessionLocal(),email=email)
    if user:
        recovery_code = create_recovery_code(db=SessionLocal(),user=user)

        send_recovery_email(recovery_code=recovery_code,to_email=email)
        return {"message": "Se ha enviado un correo electrónico con instrucciones para restablecer la contraseña."}
    else:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    


@router.post("/reset-password",description="Introduce el codigo que se le fue mandado por correo")
async def reset_password(email: str = Form(pattern="^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+"),recovery_code: int = Form(...),password:str = Form()):
    user = get_user_by_email_and_recovery_code(db=SessionLocal(),email=email,recovery_code=recovery_code)
    
    if user and user.recovery_code_expiration > datetime.utcnow() :
        # Restablecer la contraseña y limpiar el código de recuperación
        password = crypt.hash(password)
        updatae_password(db=SessionLocal(),user=user,new_password=password)
        return {"message": "Contraseña restablecida exitosamente."}
    else:
        raise HTTPException(status_code=400, detail="Código de recuperación inválido o vencido.")
        




def validar_contraseña(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres, un número y una letra mayúscula y minuscula")
    if not any(c.isupper() for c in password):
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres, un número y una letra mayúscula y minuscula")
    if not any(c.islower() for c in password):
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres, un número y una letra mayúscula y minuscula")
    if not any(c.isdigit() for c in password):
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres, un número y una letra mayúscula y minuscula")
