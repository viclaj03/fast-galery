from fastapi import FastAPI
from routers import users_routers,image_routers,coments_routers,reported_routers,message_routers
from typing import Union
from fastapi.staticfiles import StaticFiles
from database.table import *

 

app = FastAPI(title="Fast gallery",
    description="a REST API using python and mysql",
    version="0.8.1",contact={"email":"info@fastgallery.com","name":"Víctor"},summary="Te falta el REGISTRE\n Deadpool's favorite app. Nuff said.",terms_of_service="http://example.com/terms/",)

app.include_router(users_routers.router)
app.include_router(image_routers.router)
app.include_router(coments_routers.router)
app.include_router(reported_routers.router)
app.include_router(message_routers.router) 
app.mount('/static',StaticFiles(directory="static"),name="static")
 
#swaguer: http://127.0.0.1:8000/docs
#redocly: http://127.0.0.1:8000/redoc

 