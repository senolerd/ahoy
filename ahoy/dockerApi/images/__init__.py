from flask import Blueprint

docker_images_bp = Blueprint( "docker_images_bp", __name__, url_prefix='/images')

from ahoy.dockerApi.images import routes