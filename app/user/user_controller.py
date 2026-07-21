from flask import Blueprint, jsonify, request

from app.user.user_entity import UserStatus


def create_user_blueprint(user_service):
    users_bp = Blueprint("users", __name__, url_prefix="/users")

    @users_bp.post("")
    def create_user():
        data = request.get_json(silent=True) or {}

        try:
            user = user_service.create_user(
                name=data.get("name"),
                email=data.get("email"),
                cpf=data.get("cpf"),
                status=data.get("status", UserStatus.ACTIVE),
            )
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

        return jsonify(user.to_dict()), 201

    @users_bp.get("/<user_id>")
    def get_user(user_id):
        user = user_service.get_user(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user.to_dict()), 200

    @users_bp.get("")
    def list_users():
        users = user_service.list_users()
        return jsonify([user.to_dict() for user in users]), 200

    @users_bp.put("/<user_id>")
    def update_user(user_id):
        data = request.get_json(silent=True) or {}

        try:
            user = user_service.update_user(
                user_id,
                name=data.get("name"),
                email=data.get("email"),
                cpf=data.get("cpf"),
                status=data.get("status"),
            )
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

        if user is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user.to_dict()), 200

    return users_bp
