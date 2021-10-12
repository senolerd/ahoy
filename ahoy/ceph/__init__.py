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
    requested_addr = str(data['ManagerStatus']['Addr']).split(":")[0] if 'ManagerStatus' in data else data['Status']['Addr']
    requested_addr_disks_url = f"{current_app.config['AHOY_PROTO']}://{requested_addr}:{current_app.config['AHOY_PORT']}/ceph/disks"
    return json.loads(urllib3.PoolManager().request('GET' ,requested_addr_disks_url).data.decode())
    

@ceph_bp.route('/disks', methods=['GET','POST'])
def disks():

    cat_partition_cmd = ["cat","/proc/partitions"]
    cat_mounts_cmd = ["cat","/proc/mounts"]
    dmsetup_table_cmd = ["dmsetup","table"]
    dmsetup_ls_cmd = ["dmsetup","ls"]
    lvm_disks = []




    def isIgnored(major, minor, blocks, name):

        # Right of the bat ignored disks based on prefix of the disk's names
        ignored_disks_suffix = ['loop', 'mapper', "dm-"]

        for ignored_disk in ignored_disks_suffix:
            if str(name).startswith(ignored_disk):
                raise Exception
    
        # Deceting LVM partitios
        dmsetup_table  = subprocess.check_output(dmsetup_table_cmd)
        [ lvm_disks.append(dm_item.split(' ')[4]) for dm_item in dmsetup_table.decode().splitlines() if dm_item.split(' ')[4] not in lvm_disks ]  
        if f"{major}:{minor}" in lvm_disks:
            raise Exception



        print("LVM Disks: ", lvm_disks)

                

    partitions = subprocess.check_output(cat_partition_cmd).decode().split("\n")[2:-1]
    mounts = [mount.split(' ')[0] for mount in subprocess.check_output(cat_mounts_cmd).decode().split('\n')]

    disks = {}
    disk_name = ""

    for partition in partitions:
        major, minor, blocks, name = partition.split()

        try:
            isIgnored(major, minor, blocks, name)

            if int(minor) == 0:
                disks[name] = {'major': major, 'minor': minor, 'blocks': blocks, 'partitions':[]}
                disk_name = name
            
            if int(minor) > 0:
                disk_part = { name:{'major': major, 'minor': minor, 'blocks': blocks, 'usable': True if f'/dev/{name}' in mounts else False} }
                disks[disk_name]['partitions'].append(disk_part)
        except:
            pass
            

    # print(disks)
    return jsonify(disks)

