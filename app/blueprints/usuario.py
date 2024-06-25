from apiflask import Schema, abort, APIBlueprint
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask import current_app, jsonify, request
from sqlalchemy.orm import scoped_session
from ..models.alch_model import Grupo,Usuario
from ..models.usuarios_model import get_all_usuarios, get_usuario_by_id, insert_usuario
from ..schemas.schemas import  UsuarioIn, UsuarioOut
from ..common.error_handling import ValidationError

usuario_b = APIBlueprint('usuario_b', __name__)

""" @usuario_b.get('/usuario')
def get_grupos():
    session: scoped_session = current_app.session
    usuarios = session.query(Usuario).all()
    
    return jsonify([{
        'id': str(usuario.id),
        'nombre': str(usuario.nombre),
        'apellido': usuario.apellido,
        'fecha_actualizacion': usuario.fecha_actualizacion
    } for usuario in usuarios]) """

@usuario_b.get('/usuario')
@usuario_b.output(UsuarioOut(many=True))
def get_usuarios():
    try:
        res = get_all_usuarios()
        if res is None:
            result = {
                "data": res
            }
            return result
        return res
    
    except Exception as err:
        raise ValidationError(err)  
    

#################POST####################
@usuario_b.post('/usuario')
#@usuario_bp.input(UsuarioIn)
@usuario_b.output(UsuarioOut)
def post_usuario():
    try:
        request_data = request.get_json()
        print(request_data)
        res = insert_usuario(**request_data)
        if res is None:
            result = {
                "data": res
            }
            return result
        return res
    
    except Exception as err:
        raise ValidationError(err)