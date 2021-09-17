from werkzeug.wrappers import request
from docker.errors import APIError as docker_api_error
from ahoy.dockerApi import docker_client
from ahoy.dockerApi.network import docker_networks_bp
from flask import json, jsonify, request



@docker_networks_bp.route('/')
def networks_index():
    return "network_index"


@docker_networks_bp.route('/list')
def networks_list():
    net_list = []
    for network in docker_client.networks.list():
        if network.attrs['Ingress'] != True:
            net_list.append(network.attrs)

    return jsonify(net_list)


@docker_networks_bp.route('/create', methods=['GET', 'POST'])
def createNetwork():
    if request.method == 'POST':
        network_info = json.loads(request.data.decode())
        # print('Name: ',  network_info['name']  )
        try:
            docker_response = docker_client.networks.create(
                attachable=network_info['attachable'],
                driver=network_info['driver'],
                enable_ipv6=network_info['enable_ipv6'],
                ingress=network_info['ingress'],
                internal=network_info['internal'],
                name=network_info['name'],
                check_duplicate=True
            )
            return jsonify(docker_response.attrs), 200

        except docker_api_error as err:
            print(err.explanation)
            return {"error": err.explanation}, 400

    return {"error": "unknown_request_method"}, 400


@docker_networks_bp.route('/delete', methods=['GET', 'POST'])
def deleteNetwork():
    if request.method == "POST":
        try:
            net = docker_client.networks.get(request.data.decode())   
            net.remove()
            return {'success': f"{net.id} is removed."},200
        except docker_api_error as err:
            return {'error': f'{err.explanation}'}, 400


    return {"error": "unknown_request_method"}, 400
