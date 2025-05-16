from apiflask import APIBlueprint
from flask import current_app, jsonify, request
import boto3
import json
import os
from datetime import datetime
from models.tarea_model import get_tarea_grupo, get_all_tarea_detalle
from schemas.schemas import ActuacionOut, TipoActuacionOut,TareaAllOut
from common.error_handling import ValidationError

ai_assistant = APIBlueprint('ai_assistant', __name__)

@ai_assistant.post('/chat')
def chat():
    """
    Chat with AI Assistant.
    ==============

    **Chat with Claude 3.5 (Sonnet) via AWS Bedrock**
 
    :return: JSON object with assistant's response or an error message.
    :rtype: json
    """
    try:
        # Get the message from request
        data = request.get_json()

        print("data is")
        print(data)
       
        if not data or 'message' not in data:
            return jsonify({
                "error": "No message provided"
            }), 400
        if not data or 'loggedUserData' not in data:
            return jsonify({
                "error": "No loggedUserData provided"
            }), 400
        context="""Eres un asistente de sistema de gestion de tareas, el usuario te puede preguntar por informacion de sus tareas.
        El usuario pertenece a uno o mas grupos, en cada grupo puede tener una o mas tareas asignadas.
        A continuacion tendras los datos de las tareas del usuario sin finalizar ni eliminar (solo debes informar tareas abiertas o en progreso), 
        provenientes de la base de datos.
        Luego de los datos, vendran las preguntas del usuario dentro de un arreglo de mensajes, cada mensaje(objeto) tendra in "isUser" para denotar si es el mensage de usuario o tu respuesta.
        y un campo "text" con el contenido del mensaje. 
        Si no encuentras tareas, debes responder que no hay tareas asignadas al usuario.
        Debes mostrar el nombre de la tarea, la fecha de vencimiento, el estado de la tarea y a quien se encuentra asignada.
        La respuesta debe ser en lenguaje natural, en español y debe ser breve y concisa. Las distintas tareas deben mostrarse en formato de listado, numeradas según el orden de venciminento.
        una debajo de otra para mejorar la visualización.
       ( A modo de ejemplo debes indicarlas así: 
        1. titulo, Fecha de vencimiento, estado, usuario asignado.
        2. titulo, Fecha de vencimiento, estado, usuario asignado.
        3. titulo, Fecha de vencimiento, estado, usuario asignado.
        ...)
        Solo debes mostrar que no han sido finalizadas ni eliminadas (tarea_estado == 1 o 2). 
        En caso de que solicite las tareas finalizadas debes mostrar tareas en estado 3, indicando que usuario la finalizó
        No debe incluir detalles innecesarios. No debes mostrar los id de la base de datos
        No debes mostrar el formato de los datos, solo la respuesta en lenguaje natural. 
        Si el usuario indica la palabra "mis" o "mias" en el mensaje, debes mostrar solo las tareas asignadas al usuario (loggedUser['id']).
        Después del análisis, ofrece ver más detalles una tarea en particular segun el número listado (solicita que te indique el número de la tarea que desea visualizar).

        datos de tareas:
        [
            {
                id_tarea: id de la tarea
                id_grupo: id del grupo al que pertenece la tarea
                titulo: nombre de la tarea
                cuerpo: descripcion de la tarea
                estado: estado de la tarea (abierta, cerrada, en progreso)
                tipo_actuacion: tipo de actuacion de la tarea (tipo_actuacion)
                caratula_expediente: caratula expediente de la tarea
                actuacion: actuacion de la tarea (actuacion)
                fecha_creacion: fecha de creacion de la tarea
                fecha_modificacion: fecha de modificacion de la tarea
            }
        ]
        datos de tarea asignada a usuario:
        [
            {
                id_tarea: id de la tarea
                id_usuario: id del usuario asignado a la tarea
                nombre_completo: nombre completo del usuario asignado a la tarea
                fecha_asignacion: fecha de asignacion de la tarea
                fecha_vencimiento: fecha de vencimiento de la tarea
                fecha_realizacion: fecha de realizacion de la tarea
            }
        ]   
        
        """


        user_message = data['message']
        loggedUser = request.get_json()['loggedUserData']

        #check if ai_temp_data folder exists if not create it
        if not os.path.exists('ai_temp_data'):
            os.makedirs('ai_temp_data')

        #fetch all tasks related to the user and save it in a json file in the temp folder with the user id as filename
        # user_groups=[]
        # for grupo in loggedUser["grupo"]:
        #     print("ID GRUPO FOR USER")
        #     print(grupo['id_grupo'])
        user_groups = ",".join([str(grupo['id_grupo']) for grupo in loggedUser["grupo"]])        
        print("user groups")
        print(user_groups, loggedUser['id'] )
        res,cant=get_all_tarea_detalle(grupos=user_groups)
        print("got all user tasks")
        print(res)  
        print 
        date_now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(f'ai_temp_data/{loggedUser["id"]+"_"+date_now}.json', 'w') as f:
            json.dump(TareaAllOut().dump(res, many=True), f, default=str)
         
        # Initialize Bedrock Runtime client
        print("Initializing Bedrock client")
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-west-2'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )

        # Prepare the request body for Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": context+str(TareaAllOut().dump(res, many=True))+str(user_message)}] 
                }
            ]
        }

        # Invoke the model
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps(request_body)
        )

        # Parse the response
        response_body = json.loads(response.get('body').read())
        
        # Return the response
        return jsonify({
            "response": response_body['content'][0]['text']
        })

    except Exception as err:
        current_app.logger.error(f"Error in chat endpoint: {str(err)}")
        return jsonify({
            "error": str(err)
        }), 500
