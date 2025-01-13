import pika
import json
import os
from flask import current_app
from sqlalchemy.orm import scoped_session
from models.alch_model import Parametros, Usuario
from common.functions import get_user_ip
import requests
from time import sleep

def check_updates(session, entity='', action='', entity_id=None, url=''):
        print("Checking updates...")

        res = session.query(Parametros).filter(Parametros.table == entity).first()
        if not res:
            print(f"No se encontró la tabla {entity} en los parámetros.")
            return

        campos = res.columns
        print("campos: ", campos)
        if action in ["POST", "PUT"]:
            print("action: ", action)
            #usher_apikey = os.environ.get('USHER_API_KEY', 'default_apikey')
            usher_apikey = os.environ.get('USHER_API_KEY')
            #system_apikey = os.environ.get('SYSTEM_API_KEY', 'default_system')
            system_apikey = os.environ.get('SYSTEM_NAME')
            print("usher_apikey: ", usher_apikey)
            print("system_apikey: ", system_apikey)
            headers = {'x-api-key': usher_apikey, 'x-api-system':system_apikey}
            params = {"usuario_consulta": "csolanilla@mail.jus.mendoza.gov.ar"}

            try:
                entity_id = '206598a1-3fdd-45a3-81e5-45dbcc665a63'
                response = requests.get(url, params=params, headers=headers).json()
                attributes_list = response['data']
                print("#"*50)
                #print("attributes: ", attributes_list)  
                #print("tipo de attributes: ", type(attributes_list))

                attributes = next((attr for attr in attributes_list if attr.get('id') == entity_id), None)

                if not attributes:
                    print(f"No se encontró un registro en 'data' con id: {entity_id}")
                    return

                valid_attributes = {key: value for key, value in attributes.items() if key in campos}
                """ alid_attributes = [{key: value for key, value in attributes.items() if key in campos}
                                    for attributes in attributes_list] """
                
                print("valid_attributes: ", valid_attributes)

                if entity == 'usuario':
                    print("entity: ", entity)
                    query = session.query(Usuario).filter(Usuario.id_persona_ext == entity_id).first()
                    if query is not None:
                        print("Usuario encontrado, actualizando..." + entity_id)
                        for key, value in valid_attributes.items():
                            if key != 'id':
                                setattr(query, key, value)
                        session.commit()
                        print("Actualizaciones realizadas.")
                    else:
                        print("Usuario no encontrado.")

            except Exception as e:
                print("Error en check_updates:", e)

class RabbitMQHandler:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.objeto = None

    def connect(self):
        rabbitmq_params = {
            'user': os.environ.get('RABBITMQ_USER', 'guest'),
            'password': os.environ.get('RABBITMQ_PASSWORD', 'guest'),
            'host': os.environ.get('RABBITMQ_HOST', 'localhost'),
            'port': int(os.environ.get('RABBITMQ_PORT', 5672)),
            'vhost': os.environ.get('RABBITMQ_VHOST', '/')
        }

        try:
            connection_params = pika.ConnectionParameters(
                host=rabbitmq_params['host'],
                port=rabbitmq_params['port'],
                virtual_host=rabbitmq_params['vhost'],
                credentials=pika.PlainCredentials(
                    rabbitmq_params['user'], rabbitmq_params['password']
                )
            )
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='expte_params', durable=True, passive=True)
            print("RabbitMQ conectado.")
        except Exception as e:
            print("Error conectando a RabbitMQ:", e)
            self.connection, self.channel = None, None

    """ def callback(self, ch, method, properties, body):
        print(f" [x] Received {body}")
        self.objeto = json.loads(body.decode('utf-8'))
        self.process_message() """

    def callback(self, ch, method, properties, body):
        print(f" [x] Received {body}")
        self.objeto = json.loads(body.decode('utf-8'))
        with current_app.app_context():
            session = current_app.session
            self.process_message(session)

    def process_message(self, session):
        if not self.objeto:
            print("No se recibió un objeto válido.")
            return

        entity = self.objeto.get('entity_type', '').lower()
        action = self.objeto.get('action', '')
        entity_id = self.objeto.get('entity_id', '')
        url = self.objeto.get('url', '')

        print("entity: ", entity)
        print("action: ", action)
        print("entity_id: ", entity_id)
        print("url: ", url)

        check_updates(session, entity, action, entity_id, url)

    """ def process_message(self):
        if not self.objeto:
            print("No se recibió un objeto válido.")
            return

        entity = self.objeto.get('entity_type', '').lower()
        action = self.objeto.get('action', '')
        entity_id = self.objeto.get('entity_id', '')
        url = self.objeto.get('url', '')

        print("entity: ", entity)
        print("action: ", action)
        print("entity_id: ", entity_id)
        print("url: ", url)

        check_updates(entity, action, entity_id, url) """

    def start_consuming(self):
        if not self.channel:
            print("No se puede consumir mensajes sin conexión.")
            return

        self.channel.basic_consume(queue='expte_params', auto_ack=True, on_message_callback=self.callback)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("Consumo de mensajes detenido manualmente.")
        """finally:
            if self.connection:
                self.connection.close() """
    

