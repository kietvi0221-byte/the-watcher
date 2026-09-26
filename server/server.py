import os
import time
import threading

from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit


# ============================================================
# CONFIG
# ============================================================

HOST = "0.0.0.0"

PORT = int(
    os.environ.get(
        "PORT",
        5000
    )
)

# Local:
#   Nếu chưa có biến môi trường -> LOCAL-ONLY
#
# Render:
#   Đặt WATCHER_ADMIN_TOKEN trong Environment Variables
#
ADMIN_TOKEN = os.environ.get(
    "WATCHER_ADMIN_TOKEN",
    "LOCAL-ONLY"
)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_DIR = os.path.dirname(
    BASE_DIR
)

MOBILE_DIR = os.path.join(
    PROJECT_DIR,
    "mobile"
)


# ============================================================
# APP
# ============================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "WATCHER_SECRET_KEY",
    "watcher-local-secret"
)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)


# ============================================================
# DATA
# ============================================================

clients = {}

# Message cuối cùng dành cho mobile
last_mobile_message = {
    "message": "Nothing unusual.",
    "timestamp": time.time()
}


# ============================================================
# HELPERS
# ============================================================

def check_admin():

    token = request.headers.get(
        "X-Watcher-Token"
    )

    return token == ADMIN_TOKEN


def now():

    return time.time()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({
        "name": "The Watcher Server",
        "status": "online",
        "mobile": "/mobile/"
    })


# ============================================================
# MOBILE APP
# ============================================================

@app.route("/mobile/")
def mobile_index():

    return send_from_directory(
        MOBILE_DIR,
        "index.html"
    )


@app.route("/mobile/<path:filename>")
def mobile_files(filename):

    return send_from_directory(
        MOBILE_DIR,
        filename
    )


# ============================================================
# MOBILE STATUS
# ============================================================

@app.route("/api/mobile/status")
def mobile_status():

    online_clients = []

    for client_id, client in clients.items():

        if client.get("status") == "online":

            online_clients.append({
                "client_id": client_id,

                "hostname": client.get(
                    "hostname",
                    "Unknown"
                ),

                "version": client.get(
                    "version",
                    "Unknown"
                ),

                "last_seen": client.get(
                    "last_seen"
                )
            })

    return jsonify({
        "status": "online",

        "message":
            last_mobile_message["message"],

        "timestamp":
            last_mobile_message["timestamp"],

        "clients":
            online_clients
    })


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/api/register",
    methods=["POST"]
)
def register():

    if not check_admin():

        return jsonify({
            "error": "Unauthorized"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    client_id = data.get(
        "client_id"
    )

    hostname = data.get(
        "hostname",
        "Unknown"
    )

    version = data.get(
        "version",
        "Unknown"
    )

    if not client_id:

        return jsonify({
            "error": "client_id required"
        }), 400

    clients[client_id] = {

        "client_id":
            client_id,

        "hostname":
            hostname,

        "version":
            version,

        "status":
            "online",

        "last_seen":
            now(),

        "sid":
            None
    }

    return jsonify({
        "success":
            True,

        "client_id":
            client_id
    })


# ============================================================
# CLIENT LIST
# ============================================================

@app.route("/api/clients")
def client_list():

    if not check_admin():

        return jsonify({
            "error": "Unauthorized"
        }), 401

    result = []

    for client in clients.values():

        result.append({

            "client_id":
                client["client_id"],

            "hostname":
                client["hostname"],

            "version":
                client["version"],

            "status":
                client["status"],

            "last_seen":
                client["last_seen"]
        })

    return jsonify(result)


# ============================================================
# SEND MESSAGE
# ============================================================

@app.route(
    "/api/send",
    methods=["POST"]
)
def send_message():

    global last_mobile_message

    if not check_admin():

        return jsonify({
            "error": "Unauthorized"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    client_id = data.get(
        "client_id"
    )

    message = data.get(
        "message",
        ""
    )

    duration = data.get(
        "duration",
        5
    )

    effect = data.get(
        "effect",
        "normal"
    )

    if not message:

        return jsonify({
            "error":
                "message required"
        }), 400

    # ========================================================
    # SAVE FOR PHONE
    # ========================================================

    last_mobile_message = {

        "message":
            message,

        "timestamp":
            now()
    }

    # ========================================================
    # SEND TO PC
    # ========================================================

    if client_id:

        client = clients.get(
            client_id
        )

        if not client:

            return jsonify({
                "error":
                    "Client not found"
            }), 404

        sid = client.get(
            "sid"
        )

        if sid:

            socketio.emit(
                "watcher_message",

                {
                    "message":
                        message,

                    "duration":
                        duration,

                    "effect":
                        effect
                },

                to=sid
            )

    else:

        # Gửi tất cả Watcher đang online

        for client in clients.values():

            sid = client.get(
                "sid"
            )

            if sid:

                socketio.emit(
                    "watcher_message",

                    {
                        "message":
                            message,

                        "duration":
                            duration,

                        "effect":
                            effect
                    },

                    to=sid
                )

    return jsonify({

        "success":
            True,

        "message":
            message
    })


# ============================================================
# SOCKET CONNECT
# ============================================================

@socketio.event
def connect():

    print(
        "[+] Socket connected:",
        request.sid
    )


# ============================================================
# IDENTIFY
# ============================================================

@socketio.on("identify")
def identify(data):

    client_id = data.get(
        "client_id"
    )

    if not client_id:

        return

    hostname = data.get(
        "hostname",
        "Unknown"
    )

    version = data.get(
        "version",
        "Unknown"
    )

    clients[client_id] = {

        "client_id":
            client_id,

        "hostname":
            hostname,

        "version":
            version,

        "status":
            "online",

        "last_seen":
            now(),

        "sid":
            request.sid
    }

    print(
        "[+] Watcher connected:",
        hostname,
        client_id
    )

    emit(
        "identified",

        {
            "success":
                True,

            "client_id":
                client_id
        }
    )


# ============================================================
# HEARTBEAT
# ============================================================

@socketio.on("heartbeat")
def heartbeat(data):

    client_id = data.get(
        "client_id"
    )

    if not client_id:

        return

    client = clients.get(
        client_id
    )

    if not client:

        return

    client["last_seen"] = now()

    client["status"] = "online"

    client["sid"] = request.sid


# ============================================================
# DISCONNECT
# ============================================================

@socketio.event
def disconnect():

    sid = request.sid

    for client in clients.values():

        if client.get("sid") == sid:

            client["status"] = (
                "offline"
            )

            client["sid"] = None

            print(
                "[-] Watcher disconnected:",
                client.get(
                    "hostname",
                    "Unknown"
                )
            )

            break


# ============================================================
# CLEAN OFFLINE CLIENTS
# ============================================================

def cleanup_clients():

    while True:

        current = now()

        for client in clients.values():

            last_seen = client.get(
                "last_seen",
                current
            )

            if current - last_seen > 30:

                client["status"] = (
                    "offline"
                )

        time.sleep(10)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    threading.Thread(
        target=cleanup_clients,
        daemon=True
    ).start()

    print()
    print("=" * 50)
    print("        THE WATCHER SERVER")
    print("=" * 50)
    print()

    print("Local:")
    print(
        "http://127.0.0.1:5000"
    )

    print()

    print("Mobile:")
    print(
        "http://<PC-IP>:5000/mobile/"
    )

    print()

    print("=" * 50)
    print()

    socketio.run(
        app,
        host=HOST,
        port=PORT,
        allow_unsafe_werkzeug=True
    )