from concurrent.futures import thread
import os
import json
from time import sleep
from typing import Dict
from ahoy.dockerApi import docker_client, docker_client_low
from ahoy.dockerApi.images import docker_images_bp
from flask import jsonify, request, Response
from hurry.filesize import size
from docker.errors import APIError, ImageNotFound, BuildError
from io import BytesIO
import concurrent.futures
import pathlib
import threading
from  datetime import datetime, time, timedelta

build_log_file="/tmp/_image_building_status"


@docker_images_bp.route('/')
def index():
    return "index"


@docker_images_bp.route('/list')
def list():
    image_list = []
    for image in docker_client.images.list():
        image.attrs['Size'] = size(image.attrs['Size'])
        image.attrs['VirtualSize'] = size(image.attrs['VirtualSize'])
        image_list.append(image.attrs)

    return jsonify(image_list)


@docker_images_bp.route('/search/<name>')
def search(name):
    return jsonify(docker_client.images.search(name))


@docker_images_bp.route('/pull', methods=['POST'])
def pull_image():
    result = ""
    name = request.data.decode()

    try:
        if ':' in name:
            result = docker_client.images.pull(
                name.split(':')[0], tag=name.split(':')[1])
            return {"msg": f"{result.attrs['RepoTags'][0]} is added."}, 200

        else:
            result = docker_client.images.pull(name)
            return {"msg": f"{result.attrs['RepoTags'][0]} is added."}, 200

    except ImageNotFound as e:
        return {"error": e.explanation}, 404

    except Exception as e:
        return {"error": e}, 400


@docker_images_bp.route('/delete', methods=['POST'])
def delete_image():
    try:
        docker_client.images.remove(request.data.decode())
        return {"status": "true"}
    except Exception as err:
        return {"msg": f"Something went wrong while deleting image, {err}"}, 409


@docker_images_bp.route('/build', methods=["GET","POST", "DELETE"])
def build():
    if request.method == "DELETE":
        build_log_reset()
        return {"msg":f"Image uilding log deleted"}

    if request.method == "GET":
        """ Retuns latest building log"""
        with open(build_log_file, "r") as f:
            readlines = json.loads(f.readlines()[0])

            if len(readlines):
                return Response(json.dumps(readlines), mimetype='application/json')
            else:
                return {'status': "no image building job"},200

    if request.method == "POST":
        Dockerfile = ""
        tag = json.loads(request.data.decode())['tag']
        dockerfile = json.loads(request.data.decode())['dockerfile']

        # Prepairing the docker file
        for line in dockerfile:
            Dockerfile = Dockerfile+f"{line['instruction']} {line['value']} \n"
        f = BytesIO(Dockerfile.encode('utf-8'))

        if os.path.exists(build_log_file) == False:
            pathlib.Path(build_log_file).touch()

        if os.access(build_log_file, os.W_OK)== False:
            return {"error": "PermissionError for writing /tmp/_image_building_status "}, 400


        build_thread =  threading.Thread(target=build_image, kwargs={'Dockerfile':f, 'tag':tag })
        build_thread.start()
        return {"msg":f"Image building has been started for {tag}"}
        

def build_image(Dockerfile, tag):
    start_time = datetime.now()
    build_log_write({"msg":f"[{start_time.hour}: {start_time.minute}:{start_time.second}]: Image building has been started for {tag}"})

    try:
        build_response = docker_client.images.build(
            fileobj=Dockerfile, rm=True, tag=tag, nocache=True, timeout=100000000, labels={"ahoy_image": "True"})
        end_time = datetime.now()
        
        build_log_append({"msg":f"[{end_time.hour}: {end_time.minute}:{end_time.second}]:  Image building is done."})

        while True:
            try:
                output = build_response[1].__next__()
                key = [key for key in output.keys()][0]
                build_log_append({key:output[key]})
            except StopIteration:
                break

    except BuildError as e:
        build_log_append({"error":f"Building error: {e}"})
        return {"error": [f"Building error: {e}"], "code": 400}
  
    except APIError as e:
        build_log_append({"error":f"Api error: {e.explanation}"})
        return {"error": [f"Api error: {e.explanation}"], "code": 400}

def build_log_write(msg_line):
    """ msg_line format must be a dictionary as {msgLabel:msg} """

    new_log = []
    new_log.append(msg_line)

    with open(build_log_file,'w') as f:
        f.write( json.dumps(new_log) )

def build_log_append(msg_line):
    """ msg_line format must be a dictionary as {msgLabel:msg} """

    with open(build_log_file,"r") as f4r:
        current_log = [ line for line in json.loads(f4r.read()) ]

        current_log.append(msg_line)

        with open(build_log_file, "w") as f4w:
            f4w.write(json.dumps(current_log))

def build_log_reset():
    with open(build_log_file,'w') as f:
        f.write(json.dumps([]))
 
