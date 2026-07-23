from flask import Blueprint, jsonify, request


def create_totem_api_blueprint(session_service):
    totem_bp = Blueprint("totem", __name__, url_prefix="/api")

    @totem_bp.get("/qrid")
    def generate_qr():
        session = session_service.create_session()
        base_url = request.host_url.rstrip("/")
        return jsonify({"id": session.id, "url": f"{base_url}/pages/form/{session.id}"}), 200

    @totem_bp.get("/start/<session_id>")
    def start(session_id):
        return jsonify({"status": session_service.start_status(session_id)}), 200

    @totem_bp.get("/play/<session_id>")
    def play(session_id):
        return jsonify({"status": session_service.play_status(session_id)}), 200

    @totem_bp.post("/matchresult")
    def match_result():
        data = request.get_json(silent=True) or {}
        session_id = data.get("id")
        result = data.get("result")

        if not session_id:
            return jsonify({"error": "id is required"}), 400
        if not result:
            return jsonify({"error": "result is required"}), 400

        try:
            user = session_service.register_match_result(session_id, result)
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

        if user is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user.to_dict()), 200

    return totem_bp
