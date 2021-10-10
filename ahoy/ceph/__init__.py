import json
from logging import raiseExceptions
from flask import Blueprint, request, current_app
from flask.json import jsonify
from ahoy.dockerApi import docker_client
from psutil import disk_partitions, disk_usage
import subprocess
import urllib3

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


@ceph_bp.route('/getdisks', methods=['POST'])
def get_node_disks():
    
    data = json.loads(request.data.decode())

    # ahoyinfo

    requested_addr = str(data['ManagerStatus']['Addr']).split(":")[0] if 'ManagerStatus' in data else data['Status']['Addr']

    print(requested_addr)
    # requested_addr_ahoy_info = urllib3.PoolManager().request('GET', "http://"+requested_addr+ "/ahoyinfo")

    # print(requested_addr)


    # requested_addr_ahoy_info = urllib3.PoolManager().request('GET',)


    # print("Requested Addr: ", requested_addr)

    # res= urllib3.PoolManager().request('GET', current_app.config['AHOY_HOST']+ ':' + current_app.config['AHOY_PORT'] + '/ip')


    # ips = json.loads(str(res.data.decode()))

    # filtered_obj = filter(lambda x: x['address'] == current_app.config['AHOY_HOST'] ,ips)

    # print("filtered_obj: ", list(filtered_obj))

    return ""
    

@ceph_bp.route('/disks', methods=['GET','POST'])
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

    # print(disks)
    return jsonify(disks)

