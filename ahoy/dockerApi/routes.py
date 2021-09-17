from ahoy.dockerApi import docker_bp, docker_client

@docker_bp.route('/')
def docker_index():
    return "docker_api"

@docker_bp.route('/info')
def docker_info():
    return docker_client.info()

