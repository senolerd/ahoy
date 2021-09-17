from docker.errors import APIError
from flask import Blueprint, request
from flask import json
from flask.json import jsonify
from ahoy.dockerApi import docker_client


docker_volumes_bp = Blueprint('docker_volumes_bp',__name__, url_prefix='/volumes')


@docker_volumes_bp.route('/')
def volumes_index():
    return {'volumes':'root'}


@docker_volumes_bp.route('/list')
def volumes_list():
    volume_list = []
    for volume in docker_client.volumes.list():
        volume_list.append(volume.attrs)
    return jsonify(volume_list),200


@docker_volumes_bp.route('/create', methods=['POST'])
def volume_create():

    volume_id = json.loads(request.data.decode())['volume_id']
    print('Create volume: ', volume_id)

    try:
        docker_client.volumes.create(name=volume_id)
        return {'status': f"{volume_id} is created."}, 200

    except APIError as err:
        print(err.explanation)
        return {'status':err.explanation}, 400




@docker_volumes_bp.route('/delete', methods=['POST'])
def volume_delete():
    # {'volume_id': volumeName}

    volume_id = json.loads(request.data.decode())['volume_id']

    try:
        docker_client.volumes.get(volume_id=volume_id).remove()
        return {'status': f"{volume_id} is deleted."}, 200

    except APIError as err:
        print(err.explanation)
        return {'status':err.explanation}, 400
