from flask import request
from datetime import date, timedelta
from ..schemas.schemas import TareaSchema, TipoTareaSchema, TipoTareaIn, TareaOut, TipoTareaOut
from ..models.alch_model import TipoTarea, Tarea
from ..models.tarea_model import get_tareas, get_tipo_tareas, insert_tipo_tarea
from app.common.error_handling import ObjectNotFound, InvalidPayload, ValidationError
#from flask_jwt_extended import jwt_required
from apiflask import APIBlueprint


tarea_b = APIBlueprint('tarea_bp', __name__)


@tarea_b.get('/tipo_tareas')
@tarea_b.output(TipoTareaOut(many=True))
def get_tipoTarea():
    
    try:
        res = get_tipo_tareas()
    
        if res is None or len(res) == 0:
            print("No hay datos")    
            result = {
                "data": res
            }
            return result

        return res
    
    except Exception as err:
        raise ValidationError(err)    


@tarea_b.post('/tipo_tarea')
#@tarea_v1_bp.input(TipoTareaIn)
@tarea_b.output(TipoTareaOut)
def post_tipo_tarea():
    try:
       
        request_data = request.get_json()
        print(request_data)
        res = insert_tipo_tarea(**request_data)
        if res is None:
            result = {
                "data": res
            }
            return result
        return res
    
    except Exception as err:
        raise ValidationError(err)  
     

@tarea_b.get('/tarea')
@tarea_b.output(TareaOut(many=True))
def get_tareas():
    try:
        res = get_tareas()    
        if res is None or len(res) == 0:
            result = {
                "data": res
            }
            return result
        return res
    
    except Exception as err:
        raise ValidationError(err) 



      