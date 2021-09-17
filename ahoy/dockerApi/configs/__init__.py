from ahoy.dockerApi.services import services
from flask import Blueprint, request
from flask import json
from flask.json import jsonify
from ahoy.dockerApi import docker_client
from docker.errors import APIError


docker_configs_bp = Blueprint('docker_configs_bp',__name__, url_prefix='/configs')

@docker_configs_bp.route('/list')
def list():
    return jsonify([config.attrs for config in docker_client.configs.list() ])


@docker_configs_bp.route('/get', methods=['POST'])
def get():
    print("GET: ",request.data.decode())
    return {"config":"here"}


@docker_configs_bp.route('/create', methods=['POST'])
def create():
    
    print("Create Config data: ", json.loads(request.data.decode()))
    config_data = json.loads(request.data.decode())

    try:
        docker_client.configs.create(**config_data)
        return {'status': f"The config {config_data['name']} is created. "}
    except APIError as err:
        return {'error':str(err.explanation).split('=')[2]}, err.status_code


@docker_configs_bp.route('/remove', methods=['POST'])
def remove():
    config_id=request.data.decode()

    for service in docker_client.services.list():
        for svcConfig in service.attrs['Spec']['TaskTemplate']['ContainerSpec']['Configs']:
            if svcConfig['ConfigID'] == config_id: return {'error': f"{svcConfig['ConfigName']} is in use by {service.attrs['Spec']['Name']} "},400

    try:
        docker_client.api.remove_config(config_id)
        return {'msg':f'{config_id} is removed'}

    except Exception as err:
        return {'msg':'Something went wrong'}