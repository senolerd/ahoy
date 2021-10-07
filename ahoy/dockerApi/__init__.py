from flask import Blueprint
import docker

docker_client = docker.from_env()
docker_client_low = docker.APIClient(base_url='unix://var/run/docker.sock')


from ahoy.dockerApi.containers import docker_containers_bp
from ahoy.dockerApi.images import docker_images_bp
from ahoy.dockerApi.network import docker_networks_bp
from ahoy.dockerApi.swarm import docker_swarm_bp
from ahoy.dockerApi.volumes import docker_volumes_bp
from ahoy.dockerApi.services import docker_services_bp
from ahoy.dockerApi.secrets import docker_secret_bp
from ahoy.dockerApi.configs import docker_configs_bp

docker_bp = Blueprint('docker_bp', __name__,url_prefix="/docker")
docker_bp.register_blueprint(docker_containers_bp)
docker_bp.register_blueprint(docker_images_bp)
docker_bp.register_blueprint(docker_networks_bp)
docker_bp.register_blueprint(docker_swarm_bp)
docker_bp.register_blueprint(docker_volumes_bp)
docker_bp.register_blueprint(docker_services_bp)
docker_bp.register_blueprint(docker_secret_bp)
docker_bp.register_blueprint(docker_configs_bp)


from ahoy.dockerApi import routes


# ###############################
# Container
################################# 
# run
# create
# get
## list 
# prune
# commit
# kill
# logs
# pause
# reload
# remove
# rename
# restart
# start
# stats
# stop
# top
# unpause
# update
# wait

# @docker_bp.route('/container/list')
# def docker_list():
#     container_list = []
#     for container in docker_client.containers.list():
#         container_list.append(container.attrs)
#     return jsonify(container_list)


