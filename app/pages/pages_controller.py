from flask import Blueprint, render_template

from app.user.user_entity import UserStatus


def create_pages_blueprint(user_service):
    pages_bp = Blueprint("pages", __name__)

    @pages_bp.get("/")
    def index():
        return render_template("index.html")

    @pages_bp.get("/crypto-test")
    def crypto_test():
        return render_template("crypto_test.html")

    @pages_bp.get("/continue")
    def continue_page():
        return render_template("continue.html")

    @pages_bp.get("/play_error")
    def play_error_page():
        return render_template("play_error.html")

    @pages_bp.get("/pages/form/<user_id>")
    def form_page(user_id):
        if user_service.get_user(user_id) is None:
            user_service.create_blank_user(user_id, status=UserStatus.ACTIVE)
        return render_template("form.html", user_id=user_id)

    return pages_bp
