from functools import wraps
import common.logger_config as logger_config
import common.exceptions as exceptions
import common.functions as functions
import uuid
from flask import request

def to_uuid(val):
    """Intenta convertir un valor a UUID, si no es válido devuelve None."""
    try:
        return uuid.UUID(str(val))
    except (ValueError, TypeError):
        return None

def process_dict1(diccionario):
    """Convierte en UUID todos los campos id o id_XXX si son válidos."""
    for campo, valor in list(diccionario.items()):
        if campo == "id" or campo.startswith("id_"):
            uuid_convertido = to_uuid(valor)
            if uuid_convertido is None:
                return False, campo  # error
            diccionario[campo] = uuid_convertido
    return True, None    

def process_dict(diccionario, ruta=""):
    """
    Convierte en UUID todos los campos id o id_XXX si son válidos,
    incluso en estructuras anidadas, y devuelve la ruta completa del error.
    """
    for campo, valor in list(diccionario.items()):
        ruta_actual = f"{ruta}.{campo}" if ruta else campo

        if campo == "id" or campo.startswith("id_"):
            uuid_convertido = to_uuid(valor)
            if uuid_convertido is None:
                return False, ruta_actual  # Error con ruta completa
            diccionario[campo] = uuid_convertido

        elif isinstance(valor, dict):
            ok, campo_error = process_dict(valor, ruta_actual)
            if not ok:
                return False, campo_error

        elif isinstance(valor, list):
            for idx, elemento in enumerate(valor):
                if isinstance(elemento, dict):
                    ok, campo_error = process_dict(elemento, f"{ruta_actual}[{idx}]")
                    if not ok:
                        return False, campo_error

    return True, None



def check_fields():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            logger_config.logger.info("CUSTOM CHECK DECORATOR")
            print("kwargs en decorador:", kwargs)
            # 1. query_data (por ejemplo en GET)
            if "query_data" in kwargs and isinstance(kwargs["query_data"], dict):
                print("query_data en decorador:", kwargs["query_data"])
                ok, campo_error = process_dict(kwargs["query_data"])
                if not ok:
                    raise exceptions.ValidationError(
                        f"El campo '{campo_error}' no contiene un UUID válido."
                    )

            # 2. json_data (por ejemplo en POST/PUT)
            if "json_data" in kwargs and isinstance(kwargs["json_data"], dict):
                print("json_data en decorador:", kwargs["json_data"])
                ok, campo_error = process_dict(kwargs["json_data"])
                if not ok:
                    raise exceptions.ValidationError(
                        f"El campo '{campo_error}' no contiene un UUID válido."
                    )
            # 3. (Opcional) id or id_ en kwargs
            for key in list(kwargs.keys()):
                if key == "id" or key.startswith("id_"):
                    ok, campo_error = process_dict(kwargs)
                    if not ok:
                        raise exceptions.ValidationError(
                            f"El campo '{campo_error}' no contiene un UUID válido."
                        )
                    """ valor = kwargs[key]
                    uuid_val = to_uuid(valor)
                    if uuid_val is None:
                        raise exceptions.ValidationError(
                            f"El campo '{key}' debe ser un UUID válido: {valor}"
                        )
                    kwargs[key] = uuid_val """

            # 3. (Opcional) query params directos en request.args
            if request.args:
                print("request.args en decorador:", request.args)
                args_dict = request.args.to_dict()
                ok, campo_error = process_dict(args_dict)
                if not ok:
                    raise exceptions.ValidationError(
                        f"El parámetro '{campo_error}' no contiene un UUID válido."
                    )

            # 4. (Opcional) datos de formulario
            if request.form:
                form_dict = request.form.to_dict()
                ok, campo_error = process_dict(form_dict)
                if not ok:
                    raise exceptions.ValidationError(
                        f"El campo de formulario '{campo_error}' no contiene un UUID válido."
                    )

            return f(*args, **kwargs)
        return wrapped
    return decorator    



def check_fields1():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            logger_config.logger.info("CUSTOM CHECK DECORATOR")
            logger_config.logger.info("CUSTOM CHECK DECORATOR")
            query_data = kwargs.get('query_data', {})
            json_data = kwargs.get('json_data', {})

            print("query_data en decorador:", query_data)
            print("json_data en decorador:", json_data)
            if isinstance (query_data, dict):
                    for campo, valor in query_data.items():
                        print(f"Campo: {campo}, Valor: {valor}")
                        if campo =='id' or campo.startswith('id_'):
                            # Verifica si el campo es un UUID válido
                            """ if not functions.es_uuid(valor):
                                # Intenta convertir el valor a UUID
                                raise exceptions.ValidationError(
                                    f"Decorador check - El campo '{campo}' debe ser un UUID válido: {valor}"
                                ) """

                            uuid_val = to_uuid(valor)
                            if uuid_val is None:
                                raise exceptions.ValidationError(
                                    f"El campo '{campo}' debe ser un UUID válido: {valor}"
                                )
                            query_data[campo] = uuid_val
                    kwargs['query_data'] = query_data
            return f(*args, **kwargs)
        return wrapped
    return decorator