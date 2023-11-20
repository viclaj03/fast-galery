from fastapi import APIRouter,Depends,HTTPException,status
from database.connection import conn, SessionLocal, engine
from models.user import *

from schemas.user_schema import  UserCreate,UserShow
from typing import List

from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION_MINUTES = 60
ACCESS_TOKEN_DURATION_HOURS = 100
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"




router = APIRouter()

oauth2 = OAuth2PasswordBearer(tokenUrl="login",auto_error=False)

crypt = CryptContext(schemes=["bcrypt"],)


from cryptography.fernet import Fernet



router = APIRouter(tags=["users"])



#token
async def auth_user(token: str = Depends(oauth2)):
    print('aqui auth')
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
    return get_user(SessionLocal(),id)
    



    
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
        list_users = get_users(SessionLocal())
        print(list_users)
        return list_users
    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}"
    
@router.get("/user/{id}",response_model=UserShow)
async def user(id: int): 
    
    user = get_user(SessionLocal(),id)

        
    if not user:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="el usuario no se encontro")
             
        
    return user
    
    


@router.post("/registre")
async def registre(data_user: UserCreate):
   # db = SessionLocal()
    user = data_user
    
    if get_user_by_name_or_email(SessionLocal(),user.name,user.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="el usuario y correo ya ha sido registrado")
    
    try:
        data_user.password = crypt.hash(data_user.password)
        print(data_user)
        new_user = create_user(db= SessionLocal(),user=data_user)
        
        #return new_user

        access_token ={"sub":new_user.name,
                   "id":new_user.id,
                   "exp":datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION_MINUTES,hours=ACCESS_TOKEN_DURATION_HOURS)}
 

        return {"access_token":jwt.encode(access_token,SECRET_KEY,algorithm=ALGORITHM),"token_type":"bearer"}

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



@router.get("/users/me")
async def me(user:UserShow = Depends(current_user)):
        
        return user


