import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime

from flask import current_app

from .alch_model import Usuario


def get_usuario_by_id(id):
    session: scoped_session = current_app.session
    return session.query(Usuario).filter(Usuario.id == id).first()
    #return Usuario.query.filter(Usuario.id == id).first()

def get_all_usuarios():
    session: scoped_session = current_app.session
    return session.query(Usuario).all()

def insert_usuario(id='', nombre='', apellido='', id_persona_ext='', id_user_actualizacion=''):
    session: scoped_session = current_app.session
    nuevoID=uuid.uuid4()
    print(nuevoID)
    nuevo_usuario = Usuario(
        id=nuevoID,
        nombre=nombre,
        apellido=apellido,
        id_persona_ext=id_persona_ext,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )

# Añadir la instancia a la sesión y hacer commit
    session.add(nuevo_usuario)
    session.commit()
    return nuevo_usuario