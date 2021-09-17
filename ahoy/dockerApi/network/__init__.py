from flask import Blueprint

docker_networks_bp = Blueprint('docker_networks_bp', __name__, url_prefix='/networks')

from ahoy.dockerApi.network import routes