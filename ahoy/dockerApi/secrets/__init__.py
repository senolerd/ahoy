from flask import Blueprint, request
from flask import json
from flask.json import jsonify
from ahoy.dockerApi import docker_client
from docker.errors import APIError


docker_secret_bp = Blueprint('docker_secret_bp',__name__, url_prefix='/secrets')


@docker_secret_bp.route('/list')
def list():
    secrets = []
    for secret in docker_client.secrets.list():
        secrets.append(secret.attrs)
    return jsonify(secrets)


@docker_secret_bp.route('/create', methods=['POST'])
def create():
    secret_data = json.loads(request.data.decode())
    try:
        creating=docker_client.secrets.create(**secret_data)
        return {'status': f"The secret '{creating.attrs['Spec']['Name']}' is created. "}
    except APIError as err:
        return {'error':str(err.explanation).split('=')[2]}, err.status_code


@docker_secret_bp.route('/remove', methods=['POST'])
def remove():
    
    secret_id=request.data.decode()

    for service in docker_client.services.list():
        for svcSecret in  service.attrs['Spec']['TaskTemplate']['ContainerSpec']['Secrets']:
            if secret_id == svcSecret['SecretID']: return {'error': f"{svcSecret['SecretName']} in use by {service.attrs['Spec']['Name']} service."}, 400
    try:
        docker_client.secrets.get(secret_id=secret_id).remove()
        return {'status':'ok'}

    except Exception as err:
        return {'error':'Sometong went wrong.'}, 400