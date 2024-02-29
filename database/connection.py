from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_USERNAME = 'root' 
DB_PASSWORD = ''
DB_HOST = '127.0.0.1'#'db'
DB_PORT = '3306'
DB_DATABASE = 'fastgallery'

# Crear la cadena de conexión
DB_URI = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'

# Crear el motor de SQLAlchemy
engine = create_engine(DB_URI, echo=True,pool_size=20)  # El parámetro 'echo' permite ver las consultas SQL en la consola

meta_data = MetaData() 


SessionLocal = sessionmaker( autoflush=False, bind=engine)
conn = engine.connect()
 
 
Base = declarative_base()









