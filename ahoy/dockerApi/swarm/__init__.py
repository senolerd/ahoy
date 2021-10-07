from ahoy.dockerApi import docker_client
from flask import Blueprint, json, request, session, current_app
from docker.errors import APIError, NotFound

docker_swarm_bp = Blueprint('docker_swarm_bp', __name__, url_prefix="/swarm")

@docker_swarm_bp.route('/')
def swarm():
    return "swarm"

# Swarm Node
@docker_swarm_bp.route('/node/list')
def node_list():
    nodes=[]

    for node in docker_client.nodes.list():
        nodes.append(node.attrs)
    return json.jsonify(nodes)


@docker_swarm_bp.route('/attrs')
def swarm_attrs():
    try:
        return json.jsonify(docker_client.swarm.attrs),200
    except APIError as e:
        return {"error":e.explanation}, e.status_code 

@docker_swarm_bp.route('/node/update', methods=['POST'])
def node_update():
    req_node_data = json.loads(request.data.decode())
    node = docker_client.nodes.get(req_node_data['ID'])
    try:
        node.update(req_node_data['Spec'])
        return {"msg":f"{node.attrs['Description']['Hostname']} is updated"}, 200
    except APIError as e:
        return {"msg": e.explanation}, e.status_code



@docker_swarm_bp.route('/node/remove', methods=['POST'])
def node_remove():
    try:
        node_id = request.data.decode()
        docker_client.api.remove_node(node_id=node_id)
        return {"msg":f"{node_id} is removed"}, 200
    except NotFound as e:
        return {"msg":e.explanation}, e.status_code
    except APIError as e:
        return {"msg": e.explanation}, e.status_code


@docker_swarm_bp.route('/init', methods=['POST'])
def swarm_init():
    data = json.loads(request.data.decode())
    if data:
        try:
            init_response = docker_client.swarm.init(advertise_addr=data['advertise_addr'], force_new_cluster=data['force_new_cluster'])
            print('Initlatinf status: ', init_response)
            return {'status':'ok'}
        except APIError as err:
            print(err)
    return {'status':'error'}


@docker_swarm_bp.route('/leave', methods=['POST'])
def swarm_leave():
    try:
        force = json.loads(request.data.decode())['force']
        docker_client.swarm.leave(force=force)
        return {'status':'ok'}
    except APIError as err:
        return {'error':err.explanation},400

@docker_swarm_bp.route('/join', methods=['POST'])
def join():

    join_data={**json.loads(request.data.decode())}
    addr = join_data['remote_addrs']
    join_data['remote_addrs'] = [addr]

    try:
        docker_client.swarm.join(**join_data)
        return {"msg":"Joined"}, 200
    except APIError as e:
        return {"msg": e.explanation}, e.status_code



# init()
# join()
# leave()
# unlock()
# update()
# reload()
# version
# attrs
