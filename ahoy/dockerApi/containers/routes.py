import json
from ahoy.dockerApi.containers import docker_containers_bp
from ahoy.dockerApi import docker_client
from flask import jsonify, request
from docker.errors import APIError, ContainerError, InvalidArgument, NullResource


@docker_containers_bp.route('/', methods=['GET','POST'])
def container_get():
    if request.method == "POST":
        try:
            container_id = json.loads(request.data.decode())['container_id'] or None
            return docker_client.containers.get(container_id=container_id).attrs
        except NullResource as err:
            return {'error': err.args[0]}

    return {'state':"get"}


@docker_containers_bp.route('/list')
def docker_list():
    container_list = []
    for container in docker_client.containers.list(all=True):
        container_list.append(container.attrs)
    return jsonify(container_list)


@docker_containers_bp.route('/run', methods=["POST"])
def run_container():
    print(json.loads(request.data.decode())['ports'])
    # ports format {'1900/udp': 1900, '32400/tcp': 32400}
    try:
        docker_client.containers.run( **json.loads(request.data.decode()) )
        return {"status":"COntainer is created."}, 200

    except APIError as err :
        return {"error": f"API Error: {err.explanation}", },400

    except ContainerError as err:
        return {"error": f"Container configration has error(s). Check container's logs."},400
    except InvalidArgument as err:
        return {"error": f"{err}" },400
    except Exception as e:
        return {"error": f"{e}" },400


@docker_containers_bp.route('/remove', methods=["POST"])
def remove_container():
    print(request.data.decode())
    container_info = json.loads(request.data.decode())

    try:
        container = docker_client.containers.get(container_info['container_id'])
        container.remove(force=container_info['force'])
        return {"state": f"{str(container.attrs['Name']).strip('/')} is removed"}
    except APIError as err:
        return {"msg": str(err.explanation).split(':')[-1]},400
    except Exception as err:
        print(err)
        return {"msg":"Something went wrong."}


@docker_containers_bp.route('/start', methods=['POST'])
def container_start():

    if request.method == "POST":
        container_id = json.loads(request.data.decode())['container_id'] or None
        if (container_id):
            try:
                docker_client.containers.get(container_id).start()
                return {"status": f"{container_id} is started."}
            except APIError as err:
                return {"msg": str(err.explanation).split(':')[-1]},400
            except Exception as err:
                print(err)
                return {"msg":"Something went wrong."}

    return {'state':"start"}


@docker_containers_bp.route('/stop', methods=['POST'])
def container_stop():

    if request.method == "POST":
        container_id = json.loads(request.data.decode())['container_id'] or None
        if (container_id):
            try:
                docker_client.containers.get(container_id).stop()
                return {"status": f"{container_id} is stopped."}
            except APIError as err:
                return {"msg": str(err.explanation).split(':')[-1]},400
            except Exception as err:
                print(err)
                return {"msg":"Something went wrong."}

    return {'state':"stop"}




# attrs
# id
# image
# labels
# name
# short_id
# status
# attach(**kwargs)
# attach_socket(**kwargs)
# diff()
# exec_run(cmd, stdout=True, stderr=True, stdin=False, tty=False, privileged=False, user='', detach=False, stream=False, socket=False, environment=None, workdir=None, demux=False)
# export(chunk_size=2097152)
# get_archive(path, chunk_size=2097152, encode_stream=False)
# kill(signal=None)
# logs(**kwargs)
# pause()
# reload()
# resize(height, width)
# restart(**kwargs)
#### start(**kwargs)
#### stop(**kwargs)
# stats(**kwargs)
# top(**kwargs)
# unpause()
# update(**kwargs)
# wait(**kwargs)



########################################################################################################
########################################################################################################
########################################################################################################
# attrs

# id

#     The ID of the object.

# image

#     The image of the container.

# labels

#     The labels of a container as dictionary.

# name

#     The name of the container.

# short_id

#     The ID of the object, truncated to 10 characters.

# status

#     The status of the container. For example, running, or exited. The raw representation of this object from the server.

# attach(**kwargs)

#     Attach to this container.

#     logs() is a wrapper around this method, which you can use instead if you want to fetch/stream container output without first retrieving the entire backlog.
#     Parameters:	

#         stdout (bool) – Include stdout.
#         stderr (bool) – Include stderr.
#         stream (bool) – Return container output progressively as an iterator of strings, rather than a single string.
#         logs (bool) – Include the container’s previous output.

#     Returns:	

#     By default, the container’s output as a single string.

#     If stream=True, an iterator of output strings.

#     Raises:	

#     docker.errors.APIError – If the server returns an error.

# attach_socket(**kwargs)

#     Like attach(), but returns the underlying socket-like object for the HTTP request.
#     Parameters:	

#         params (dict) – Dictionary of request parameters (e.g. stdout, stderr, stream).
#         ws (bool) – Use websockets instead of raw HTTP.

#     Raises:	

#     docker.errors.APIError – If the server returns an error.

# commit(repository=None, tag=None, **kwargs)

#     Commit a container to an image. Similar to the docker commit command.
#     Parameters:	

#         repository (str) – The repository to push the image to
#         tag (str) – The tag to push
#         message (str) – A commit message
#         author (str) – The name of the author
#         changes (str) – Dockerfile instructions to apply while committing
#         conf (dict) –

#         The configuration for the container. See the Engine API documentation for full details.

#     Raises:	

#     docker.errors.APIError – If the server returns an error.

# diff()

#     Inspect changes on a container’s filesystem.
#     Returns:	(str)
#     Raises:	docker.errors.APIError – If the server returns an error.

# exec_run(cmd, stdout=True, stderr=True, stdin=False, tty=False, privileged=False, user='', detach=False, stream=False, socket=False, environment=None, workdir=None, demux=False)

#     Run a command inside this container. Similar to docker exec.
#     Parameters:	

#         cmd (str or list) – Command to be executed
#         stdout (bool) – Attach to stdout. Default: True
#         stderr (bool) – Attach to stderr. Default: True
#         stdin (bool) – Attach to stdin. Default: False
#         tty (bool) – Allocate a pseudo-TTY. Default: False
#         privileged (bool) – Run as privileged.
#         user (str) – User to execute command as. Default: root
#         detach (bool) – If true, detach from the exec command. Default: False
#         stream (bool) – Stream response data. Default: False
#         socket (bool) – Return the connection socket to allow custom read/write operations. Default: False
#         environment (dict or list) – A dictionary or a list of strings in the following format ["PASSWORD=xxx"] or {"PASSWORD": "xxx"}.
#         workdir (str) – Path to working directory for this exec session
#         demux (bool) – Return stdout and stderr separately

#     Returns:	

#     A tuple of (exit_code, output)

#         exit_code: (int):

#             Exit code for the executed command or None if either stream or socket is True.
#         output: (generator, bytes, or tuple):

#             If stream=True, a generator yielding response chunks. If socket=True, a socket object for the connection. If demux=True, a tuple of two bytes: stdout and stderr. A bytestring containing response data otherwise.

#     Return type:	

#     (ExecResult)
#     Raises:	

#     docker.errors.APIError – If the server returns an error.

# export(chunk_size=2097152)

#     Export the contents of the container’s filesystem as a tar archive.
#     Parameters:	chunk_size (int) – The number of bytes returned by each iteration of the generator. If None, data will be streamed as it is received. Default: 2 MB
#     Returns:	The filesystem tar archive
#     Return type:	(str)
#     Raises:	docker.errors.APIError – If the server returns an error.

# get_archive(path, chunk_size=2097152, encode_stream=False)

#     Retrieve a file or folder from the container in the form of a tar archive.
#     Parameters:	

#         path (str) – Path to the file or folder to retrieve
#         chunk_size (int) – The number of bytes returned by each iteration of the generator. If None, data will be streamed as it is received. Default: 2 MB
#         encode_stream (bool) – Determines if data should be encoded (gzip-compressed) during transmission. Default: False

#     Returns:	

#     First element is a raw tar data stream. Second element is a dict containing stat information on the specified path.
#     Return type:	

#     (tuple)
#     Raises:	

#     docker.errors.APIError – If the server returns an error.

#     Example

#     >>> f = open('./sh_bin.tar', 'wb')
#     >>> bits, stat = container.get_archive('/bin/sh')
#     >>> print(stat)
#     {'name': 'sh', 'size': 1075464, 'mode': 493,
#      'mtime': '2018-10-01T15:37:48-07:00', 'linkTarget': ''}
#     >>> for chunk in bits:
#     ...    f.write(chunk)
#     >>> f.close()

# kill(signal=None)

#     Kill or send a signal to the container.
#     Parameters:	signal (str or int) – The signal to send. Defaults to SIGKILL
#     Raises:	docker.errors.APIError – If the server returns an error.

# logs(**kwargs)

#     Get logs from this container. Similar to the docker logs command.

#     The stream parameter makes the logs function return a blocking generator you can iterate over to retrieve log output as it happens.
#     Parameters:	

#         stdout (bool) – Get STDOUT. Default True
#         stderr (bool) – Get STDERR. Default True
#         stream (bool) – Stream the response. Default False
#         timestamps (bool) – Show timestamps. Default False
#         tail (str or int) – Output specified number of lines at the end of logs. Either an integer of number of lines or the string all. Default all
#         since (datetime or int) – Show logs since a given datetime or integer epoch (in seconds)
#         follow (bool) – Follow log output. Default False
#         until (datetime or int) – Show logs that occurred before the given datetime or integer epoch (in seconds)

#     Returns:	

#     Logs from the container.
#     Return type:	

#     (generator or str)
#     Raises:	

#     docker.errors.APIError – If the server returns an error.

# pause()

#     Pauses all processes within this container.
#     Raises:	docker.errors.APIError – If the server returns an error.

# put_archive(path, data)

#     Insert a file or folder in this container using a tar archive as source.
#     Parameters:	

#         path (str) – Path inside the container where the file(s) will be extracted. Must exist.
#         data (bytes) – tar data to be extracted

#     Returns:	

#     True if the call succeeds.
#     Return type:	

#     (bool)
#     Raises:	

#     APIError If an error occurs.

# reload()

#     Load this object from the server again and update attrs with the new data.

# remove(**kwargs)

#     Remove this container. Similar to the docker rm command.
#     Parameters:	

#         v (bool) – Remove the volumes associated with the container
#         link (bool) – Remove the specified link and not the underlying container
#         force (bool) – Force the removal of a running container (uses SIGKILL)

#     Raises:	

#     docker.errors.APIError – If the server returns an error.

# rename(name)

#     Rename this container. Similar to the docker rename command.
#     Parameters:	name (str) – New name for the container
#     Raises:	docker.errors.APIError – If the server returns an error.

# resize(height, width)

#     Resize the tty session.
#     Parameters:	

#         height (int) – Height of tty session
#         width (int) – Width of tty session

#     Raises:	

#     docker.errors.APIError – If the server returns an error.

# restart(**kwargs)

#     Restart this container. Similar to the docker restart command.
#     Parameters:	timeout (int) – Number of seconds to try to stop for before killing the container. Once killed it will then be restarted. Default is 10 seconds.
#     Raises:	docker.errors.APIError – If the server returns an error.

# start(**kwargs)

#     Start this container. Similar to the docker start command, but doesn’t support attach options.
#     Raises:	docker.errors.APIError – If the server returns an error.

# stats(**kwargs)

#     Stream statistics for this container. Similar to the docker stats command.
#     Parameters:	

#         decode (bool) – If set to true, stream will be decoded into dicts on the fly. Only applicable if stream is True. False by default.
#         stream (bool) – If set to false, only the current stats will be returned instead of a stream. True by default.

#     Raises:	

#     docker.errors.APIError – If the server returns an error.

# stop(**kwargs)

#     Stops a container. Similar to the docker stop command.
#     Parameters:	timeout (int) – Timeout in seconds to wait for the container to stop before sending a SIGKILL. Default: 10
#     Raises:	docker.errors.APIError – If the server returns an error.

# top(**kwargs)

#     Display the running processes of the container.
#     Parameters:	ps_args (str) – An optional arguments passed to ps (e.g. aux)
#     Returns:	The output of the top
#     Return type:	(str)
#     Raises:	docker.errors.APIError – If the server returns an error.

# unpause()

#     Unpause all processes within the container.
#     Raises:	docker.errors.APIError – If the server returns an error.

# update(**kwargs)

#     Update resource configuration of the containers.
#     Parameters:	

#         blkio_weight (int) – Block IO (relative weight), between 10 and 1000
#         cpu_period (int) – Limit CPU CFS (Completely Fair Scheduler) period
#         cpu_quota (int) – Limit CPU CFS (Completely Fair Scheduler) quota
#         cpu_shares (int) – CPU shares (relative weight)
#         cpuset_cpus (str) – CPUs in which to allow execution
#         cpuset_mems (str) – MEMs in which to allow execution
#         mem_limit (int or str) – Memory limit
#         mem_reservation (int or str) – Memory soft limit
#         memswap_limit (int or str) – Total memory (memory + swap), -1 to disable swap
#         kernel_memory (int or str) – Kernel memory limit
#         restart_policy (dict) – Restart policy dictionary

#     Returns:	

#     Dictionary containing a Warnings key.
#     Return type:	

#     (dict)
#     Raises:	

#     docker.errors.APIError – If the server returns an error.

# wait(**kwargs)

#     Block until the container stops, then return its exit code. Similar to the docker wait command.
#     Parameters:	

#         timeout (int) – Request timeout
#         condition (str) – Wait until a container state reaches the given condition, either not-running (default), next-exit, or removed

#     Returns:	

#     The API’s response as a Python dictionary, including

#         the container’s exit code under the StatusCode attribute.

#     Return type:	

#     (dict)
#     Raises:	

#         requests.exceptions.ReadTimeout – If the timeout is exceeded.
#         docker.errors.APIError – If the server returns an error.

