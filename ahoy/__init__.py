import re
from flask import Flask, config
from flask import json, request
from flask.json import jsonify
import psutil,pam, jwt
from requests.sessions import requote_uri
from ahoy.dockerApi import docker_bp
from flask_cors import CORS
from psutil import net_if_addrs
from flask_login import LoginManager



app = Flask(__name__, static_url_path="", static_folder="static")
CORS(app)
app.secret_key = "super secret password"

login_manager = LoginManager()
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    print("User loader is run")
    return True

app.register_blueprint(docker_bp)

# @app.before_request
# def before_any_request():
#     print(f"request for :{request.url}, token: {request.headers.get('token')}" )
#     return None


@app.route('/login', methods=["POST"])
def login():
    p = pam.pam()

    request_data_dict = dict(json.loads(request.data.decode()))
    # print("Heeaders: ",request.headers)
    # print("Data: ",request.data)

    username = request_data_dict.get("username")
    password = request_data_dict.get("password")


    if p.authenticate(username, password):
        token = jwt.encode({"user":username}, app.config["SECRET_KEY"], algorithm="HS256")
        return {"token":token},200
    else:
        return {"status":"fail"},401


@app.route('/validate')
def validate():
    token = request.headers.get('token')
    try:
        tokenPayload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        print("TOKENS USER: ", tokenPayload)
        return tokenPayload,200
    except Exception as e:
        print('ERROR' , e)
        return {"status":"err"},401


@app.route('/')
def hello_world():
    return app.send_static_file('index.html')


@app.route('/ip')
def ip_addresses():
    iflist = []
    for addr in net_if_addrs():


        if (net_if_addrs()[addr][0].netmask != None and net_if_addrs()[addr][0].broadcast != None and addr[0:6] != "docker"):
            interface = {
                "interface": addr,
                "address": net_if_addrs()[addr][0].address,
                "netmask": net_if_addrs()[addr][0].netmask,
                "broadcast": net_if_addrs()[addr][0].broadcast,
            }

            iflist.append(interface)
    return jsonify(iflist)


@app.route('/portcheck/<port>')
def checkport(port):
    print("XXX: ",  psutil.net_if_addrs()   )

    return "ok"


# def port_check(ip_port):
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.settimeout(1)
#     r = s.connect_ex(ip_port)
#     return r == 0