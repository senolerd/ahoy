from datetime import date, timedelta
import datetime
import json
import logging
from time import sleep
from ahoy.dockerApi import docker_client
from ahoy.dockerApi.images import docker_images_bp
from flask import jsonify, request, current_app, Response, g
from hurry.filesize import size
from docker.errors import APIError, ImageNotFound, BuildError
from io import BytesIO
import concurrent.futures

# @docker_images_bp.before_app_first_request
# def before_first_request():
#     try:
#         print("before_app_first_request :: ", current_app.image_building_status)
#     except Exception as _:
#         current_app.image_building_status=None


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
            print('download with tag')
            result = docker_client.images.pull(
                name.split(':')[0], tag=name.split(':')[1])
            print(result.attrs['RepoTags'][0])
            return {"msg": f"{result.attrs['RepoTags'][0]} is added."}, 200

        else:
            print('download for search')
            result = docker_client.images.pull(name)
            return {"msg": f"{result.attrs['RepoTags'][0]} is added."}, 200

    except ImageNotFound as e:
        return {"error": e.explanation}, 404

    except Exception as e:
        print(e.args)
        return {"error": e}, 400


@docker_images_bp.route('/delete', methods=['POST'])
def delete_image():
    try:
        print("Image to remove: ", request.data.decode())
        docker_client.images.remove(request.data.decode())
        return {"status": "true"}
    except Exception as err:
        print(err)
        return {"msg": f"Something went wrong while deleting image, {err}"}, 409




@docker_images_bp.route('/build', methods=["GET","POST"])
def build():

    def updateImageStatus(msg):
        # print("Update is run!!")
        with open('/tmp/_image_building_status','w') as f:
            f.write(json.dumps(msg))

    if request.method == "GET":
        status=''
        try:
            with open('/tmp/_image_building_status','r') as f:
                content = f.readline()
                # print("content: ",content)
                if content.__len__() > 0: status = content 
        except:
            pass

        if status:
            # print(status)
            return jsonify(json.loads(status))
        else:
            print("Errore")
            return {"msg": "No image found on building ", "code": 200}
            


    if request.method == "POST":
        building_log=[]
        updateImageStatus(building_log) 
        
        Dockerfile = ""
        tag = json.loads(request.data.decode())['tag']
        dockerfile = json.loads(request.data.decode())['dockerfile']

        # Prepairing the docker file
        for line in dockerfile:
            Dockerfile = Dockerfile+f"{line['instruction']} {line['value']} \n"
        f = BytesIO(Dockerfile.encode('utf-8'))

        building_log.append({ "msg": [f"Building is started for {tag}"], "code": 200})
        updateImageStatus(building_log) 

        with concurrent.futures.ThreadPoolExecutor() as executor:
            thread = executor.submit(build_image, Dockerfile=f,  tag=tag)
            result = thread.result()

            print('Result: ', result)

            building_log.append(result)
            updateImageStatus(building_log) 

        return {"status": "building is started"}

#####################


def build_image(Dockerfile, tag):

    try:
        print('building is started.')

        build_response = docker_client.images.build(
            fileobj=Dockerfile, rm=True, tag=tag, labels={"ahoy_image": "True"})

        build_log = []
        for line in build_response[1]:
            if "stream" in line: print('STREAM: ', build_log.append(str(line['stream']).strip()))
           
        print('building is end.')
        return {"msg": build_log, "code": 200}

    except BuildError as e:
        print('Building error...')
        return {"error": [f"Building error: {e}"], "code": 400}
  
    except APIError as e:
        print('Api error...')
        return {"error": [f"Api error: {e.explanation}"], "code": 400}
