
###################################################


python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

AHOY_PORT=4444
AHOY_HOST=$(python3 -c "import docker;docker_client=docker.from_env();print(docker_client.info()['Swarm']['NodeAddr'])")

export AHOY_PORT=$AHOY_PORT
export AHOY_HOST=$AHOY_HOST

gunicorn -w 12 --timeout 180 -b $AHOY_HOST:$AHOY_PORT ahoy:app --reload --log-level INFO
