
from sqlalchemy.orm import Session
from models.comment import Coment

#Aqui gestionamos el CRUD de los comentarios


#Para obtner un comentario
def get_coment(db:Session,id:int):
    return db.query(Coment).filter(Coment.id == id).first()

#Obtner los comentarios de un posts de forma paginada
def get_coments_by_id_post(db:Session, id:int,page:int, per_page: int = 8):
    start_index = (page - 1) * per_page
    
    coment_query = db.query(Coment).filter(Coment.post_id == id).offset(start_index).limit(per_page).all()
    return  coment_query

#Añade un comentario a un post
def add_coment_to_post(db:Session, id_post:int,content:str,user_id:int):
        

    db_coment = Coment(post_id=id_post,
                     user_id=user_id,
                     content=content)
    db.add(db_coment)
    db.commit()
    db.refresh(db_coment)
    return  db_coment

#elimina el comentario selecionado
def delete_comet_post(db:Session, id_coment:int):
    db_coment = db.query(Coment).filter(Coment.id ==id_coment).first()
    db.delete(db_coment)
    db.commit()
    return {'status':"ok"}