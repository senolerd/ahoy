import json
from logging import raiseExceptions
from flask import Blueprint, request
from flask.json import jsonify
import requests
from ahoy.dockerApi import docker_client
from psutil import disk_partitions, disk_usage
import os
import subprocess


ceph_bp = Blueprint('cepn_blueprint',__name__,url_prefix='/ceph')

@ceph_bp.route('/')
def index():
    return "ceph index"


@ceph_bp.route('/nodes')
def ceph_nodes():
    ceph_nodes=[]
    for node in docker_client.nodes.list():
         if 'ceph' in  node.attrs['Spec']['Labels']:
             if str(node.attrs['Spec']['Labels']['ceph']).lower() == "true":
                    ceph_nodes.append(node.attrs)

    return jsonify(ceph_nodes)



@ceph_bp.route('/all_disks')
def all_disks():
    print(request.host_url)
    # for node in json.loads(ceph_nodes().get_data().decode()):
    #     print(node['Status']['Addr'])



    return "all disks"


@ceph_bp.route('/disks')
def disks():
    ignored_disks = ['loop', 'mapper','dm']
    def isIgnorede(disk_name):
        for banned_word in ignored_disks:
            if str(disk_name).startswith(banned_word):
                return False
        

    cat_partition = ["cat","/proc/partitions"]
    cat_mounts = ["cat","/proc/mounts"]

    partitions = subprocess.check_output(cat_partition).decode().split("\n")[2:-1]
    mounts = [mount.split(' ')[0] for mount in subprocess.check_output(cat_mounts).decode().split('\n')]

    disks = {}
    disk_name = ""

    for partition in partitions:
        major, minor, blocks, name = partition.split()

        try:
            if isIgnorede(name) == False:
                raise Exception

            if int(minor) == 0:
                disks[name] = {'major': major, 'minor': minor, 'blocks': blocks, 'partitions':{}}
                disk_name = name

            if int(minor) > 0:
                disks[disk_name]['partitions'][name] = {'major': major, 'minor': minor, 'blocks': blocks, 'mounted': True if f'/dev/{name}' in mounts else False}
        except:
            pass
            
    # for disk in disks:
    #     print(disk, disks[disk]) 
    #     print('--------------')

    # print(mounts)

    print(disks)
    return jsonify(disks)

