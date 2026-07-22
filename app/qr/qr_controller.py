import uuid

from flask import Blueprint, jsonify, request

qr_bp = Blueprint("qr", __name__, url_prefix="/api")


@qr_bp.get("/qrid")
def generate_qr():
    new_id = str(uuid.uuid4())
    base_url = request.host_url.rstrip("/")
    return jsonify({"id": new_id, "url": f"{base_url}/pages/form/{new_id}"}), 200


def create_qr_status_blueprint(user_service):
    qr_status_bp = Blueprint("qr_status", __name__)

    @qr_status_bp.get("/start/<user_id>")
    def start(user_id):
        user = user_service.get_user(user_id)
        if user is None:
            return jsonify({"status": "inactive"}), 200
        return jsonify({"status": user.status.value}), 200

    return qr_status_bp
