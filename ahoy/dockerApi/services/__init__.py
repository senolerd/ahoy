import re
from docker.errors import APIError
from flask import Blueprint, json, jsonify, request
from ahoy.dockerApi import docker_client
import inspect


docker_services_bp = Blueprint(
    'docker_services_bp', __name__, url_prefix='/services')


@docker_services_bp.route('/list')
@docker_services_bp.route('/')
def services():
    return jsonify([service.attrs for service in docker_client.services.list()]), 200


@docker_services_bp.route('/tasks', methods=["GET", "POST"])
def tasks():
    data = request.data.decode()

    if request.method == "GET":
        return jsonify(docker_client.api.tasks())

    if request.method == "POST":
        service_id = request.data.decode()
        tasks = docker_client.api.tasks()

        return jsonify([filtered_task for filtered_task in tasks if filtered_task["ServiceID"] == service_id])


@docker_services_bp.route('/remove', methods=['POST'])
def remove():

    try:
        service_id = json.loads(request.data.decode())['service_id']
        service = docker_client.services.get(service_id=service_id)
        service.remove()

        return {"result": "ok"}
    except Exception as err:
        return {"err": err}


@docker_services_bp.route('/create', methods=["POST"])
def create():
    
    service = json.loads(request.data.decode())

    ## Replica convetion
    replicas = service['mode']['replicas'] if service['mode']['mode'] == "replicated" else 0
    service['mode'] = {service['mode']['mode']: {'replicas': int(replicas)}}

    try:
        docker_client.services.create(**service)
        return {"action": "create"}
    except APIError as e:
        print(e)
        return {'msg':str(e.explanation)},400
    except Exception as e:
        print(e)
        return {'msg':"Something went wrong!"},401

