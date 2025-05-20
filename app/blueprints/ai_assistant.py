from apiflask import APIBlueprint
from common.bedrock_service import invoke_bedrock_model
from flask import request, jsonify, current_app
from common.auth import verify_header
from common.error_handling import ValidationError
from models.tarea_model import get_all_tarea_detalle
from schemas.tarea_schema import TareaAllOut
from flask import g
from decorators.role import require_role


ai_assistant_b = APIBlueprint('ai_assistant_blueprint', __name__)


@ai_assistant.post('/chat')
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400
        if not data or 'loggedUserData' not in data:
            return jsonify({"error": "No loggedUserData provided"}), 400

        user_message = data['message']
        loggedUser = data['loggedUserData']

        # Fetch tasks and prepare context
        user_groups = ",".join([str(grupo['id_grupo']) for grupo in loggedUser["grupo"]])
        res, _ = get_all_tarea_detalle(grupos=user_groups)

        context = "Eres un asistente de sistema de gestion de tareas..."  # Simplified for brevity
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{context}{json.dumps(TareaAllOut().dump(res, many=True))}{user_message}"
                        }
                    ]
                }
            ]
        }

        # Call Bedrock
        response_body = invoke_bedrock_model(
            model_id='anthropic.claude-3-sonnet-20240229-v1:0',
            request_body=request_body
        )

        return jsonify({"response": response_body['content'][0]['text']})

    except Exception as err:
        current_app.logger.error(f"Error in chat endpoint: {str(err)}")
        return jsonify({"error": str(err)}), 500