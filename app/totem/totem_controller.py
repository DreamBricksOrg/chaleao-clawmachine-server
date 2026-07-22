import uuid

from flask import Blueprint, jsonify, request


def create_totem_api_blueprint(user_service):
    totem_bp = Blueprint("totem", __name__, url_prefix="/api")

    @totem_bp.get("/qrid")
    def generate_qr():
        new_id = str(uuid.uuid4())
        base_url = request.host_url.rstrip("/")
        return jsonify({"id": new_id, "url": f"{base_url}/pages/form/{new_id}"}), 200

    @totem_bp.get("/play/<user_id>")
    def play(user_id):
        user = user_service.get_user(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"status": user.status.value}), 200

    @totem_bp.post("/matchresult")
    def match_result():
        data = request.get_json(silent=True) or {}
        user_id = data.get("id")
        result = data.get("result")

        try:
            user = user_service.register_match_result(user_id, result)
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

        if user is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user.to_dict()), 200

    return totem_bp


def create_totem_status_blueprint(user_service):
    totem_status_bp = Blueprint("totem_status", __name__)

    @totem_status_bp.get("/start/<user_id>")
    def start(user_id):
        user = user_service.get_user(user_id)
        if user is None:
            return jsonify({"status": "inactive"}), 200
        return jsonify({"status": user.status.value}), 200

    return totem_status_bp
