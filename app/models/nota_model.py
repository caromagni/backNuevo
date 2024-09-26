import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime, timedelta
from ..common.functions import controla_fecha

from flask import current_app

from .alch_model import Nota, TipoNota, Usuario, TareaAsignadaUsuario, Grupo, TareaXGrupo, Inhabilidad


def insert_nota(titulo='', nota='', id_tipo_nota=None, eliminado=False, fecha_eliminacion=None, fecha_actualizacion=None, id_user_creacion=None,  fecha_creacion=None, id_tarea=None):
    session: scoped_session = current_app.session
   

    ########################################################
    
    print("Usuario:", nota)
    #fecha_inicio = controla_fecha(fecha_inicio)
    #fecha_fin = controla_fecha(fecha_fin)   
    print("fecha_inicio:",fecha_creacion)
    tipo_nota = session.query(TipoNota).filter(TipoNota.id == id_tipo_nota).first()
    if tipo_nota is None:
       msg = "Tipo de nota no encontrado"
       return None, msg

    nuevoID_nota=uuid.uuid4()

    nueva_nota = Nota(
        id=nuevoID_nota,
        titulo=titulo,
        nota=nota,
        id_tipo_nota=id_tipo_nota,
        id_tarea=id_tarea,
        eliminado=eliminado,
        id_user_creacion=id_user_creacion,
        fecha_creacion=datetime.now(),
        fecha_eliminacion=fecha_eliminacion,
        fecha_actualizacion=fecha_actualizacion
    )

    session.add(nueva_nota)
       
    session.commit()
    return nueva_nota

def update_nota(id='', **kwargs):
    ################################
    session: scoped_session = current_app.session
    nota = session.query(Nota).filter(Nota.id == id, Nota.eliminado==False).first()
   
    if nota is None:
        return None
    
    if 'eliminado' in kwargs:
        nota.eliminado = kwargs['eliminado']
    if 'id_tarea' in kwargs:
        nota.id_tarea = kwargs['id_tarea']           
    if 'id_tipo_nota' in kwargs:
        nota.id_tipo_nota = kwargs['id_tipo_nota']
    if 'nota' in kwargs:
        nota.nota = kwargs['nota']
    if 'titulo' in kwargs:
        nota.titulo = kwargs['titulo'].upper()  
        
    nota.fecha_actualizacion = datetime.now()
    

    ###################Formatear el resultado####################
    result = {
        "id": nota.id,
        "titulo": nota.titulo,
        "id_tipo_nota": nota.id_tipo_nota,
        "tipo_nota": nota.tipo_nota,
        "id_tarea": nota.id_expediente,
        "nota": nota.nota,
        "eliminado": nota.eliminado,
        "fecha_eliminacion": nota.fecha_eliminacion,
        "fecha_actualizacion": nota.fecha_actualizacion,
        "fecha_creacion": nota.fecha_creacion,
        
    }

    session.commit()
    return result

def get_all_tipo_nota(page=1, per_page=10):
    print("get_tipo_notas - ", page, "-", per_page)
    session: scoped_session = current_app.session
    todo = session.query(TipoNota).all()
    total= len(todo)
    res = session.query(TipoNota).order_by(TipoNota.nombre).offset((page-1)*per_page).limit(per_page).all()
    return res, total

def insert_tipo_nota(id='', nombre='', id_user_actualizacion='', habilitado=True, eliminado=False):
    session: scoped_session = current_app.session
    nuevoID=uuid.uuid4()
    nuevo_tipo_nota = TipoNota(
        id=nuevoID,
        nombre=nombre,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now(),
        fecha_eliminacion=datetime.now(),
        habilitado=True,
        eliminado=False
    )

    session.add(nuevo_tipo_nota)
    session.commit()
    return nuevo_tipo_nota

def delete_tipo_nota(id):
    session: scoped_session = current_app.session
    tipo_nota = session.query(TipoNota).filter(TipoNota.id == id, TipoNota.eliminado==False).first()
    if tipo_nota is not None:
        tipo_nota.eliminado=True
        tipo_nota.fecha_actualizacion=datetime.now()
        session.commit()
        return tipo_nota
    else:
        print("Tipo de nota no encontrado")
        return None
    

##########################NOTAS #############################################


def get_nota_by_id(id):
    session: scoped_session = current_app.session
    
    res = session.query(Nota).filter(Nota.id == id).first()
    if res is not None:
        return res 

    else:
        print("Nota no encontrada")
        return None
    
    """ results = []
    tipos_nota=[]
 

    if res is not None:
        #Consulto los tipos de las tareas
        print("Nota encontrada:", res)
        res_tipos_nota = session.query(tipo_nota.id_tipo_nota, tipo_nota.nombre, tipo_nota.apellido
                                  ).join(res.tipo_nota, tipo_nota.id==res.tipo_nota.id_tipo_nota).filter(res.tipo_nota.id_nota== res.id).all()
        
        
        if res_tipos_nota is not None:
            for row in res_tipos_nota:
                tipo_nota = {
                    "id": row.id,
                    "nombre": row.nombre,
                    "habilitado": row.habilitado
                }
                tipos_nota.append(tipo_nota)


        ###################Formatear el resultado####################
        result = {
            "id": res.id,
            "titulo": res.titulo,
            "id_tipo_nota": res.id_tipo_nota,
            "tipo_nota": res.tipo_nota,
            "nota": res.nota,
            "eliminado": res.eliminado,
            "fecha_eliminacion": res.fecha_eliminacion,
            "fecha_creacion": res.fecha_creacion,
            "fecha_actualizacion": res.fecha_actualizacion,
            "usuario": usuario
        }

        results.append(result) """
   
   


def get_all_nota(page=1, per_page=10, titulo='', id_tipo_nota=None, id_tarea=None, id_user_creacion=None, fecha_desde='01/01/2000', fecha_hasta=datetime.now(), eliminado=None):
    session: scoped_session = current_app.session
    query = session.query(Nota).filter(Nota.fecha_creacion.between(fecha_desde, fecha_hasta))
    print(query)
    if titulo != '':
        query = query.filter(Nota.titulo.ilike(f'%{titulo}%'))

    if id_tipo_nota is not None:
        query = query.filter(Nota.id_tipo_nota== id_tipo_nota)

    if id_tarea is not None:
        query = query.filter(Nota.id_tarea== id_tarea)

    if id_user_creacion is not None:
        query = query.filter(Nota.id_user_creacion == id_user_creacion)

    if eliminado is not None:
        query = query.filter(Nota.eliminado == eliminado)

    #muestra datos
    print("Query:", query.all())
    total= len(query.all()) 

    result = query.order_by(Nota.fecha_creacion).offset((page-1)*per_page).limit(per_page).all()
    
    return result, total


def delete_nota(id_nota):
    session: scoped_session = current_app.session
    nota = session.query(Nota).filter(Nota.id == id_nota, Nota.eliminado==False).first()
    if nota is not None:              
        nota.eliminado=True
        nota.fecha_eliminacion=datetime.now()
        nota.fecha_actualizacion=datetime.now()
        session.commit()
        return nota
    
    else:
        print("Nota no encontrada")
        return None
    



