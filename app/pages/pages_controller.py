from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from app.user.user_entity import UserStatus

COOKIE_NAME = "user_id"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # 1 ano


def create_pages_blueprint(user_service):
    pages_bp = Blueprint("pages", __name__, url_prefix="/pages")

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

    @pages_bp.get("/form/<user_id>")
    def form_page(user_id):
        known_user_id = request.cookies.get(COOKIE_NAME)
        if known_user_id:
            known_user = user_service.get_user(known_user_id)
            if known_user is not None:
                if known_user.can_play():
                    user_service.mark_play_again(known_user)
                    return redirect(url_for("pages.continue_page"))
                return redirect(url_for("pages.play_error_page"))

        if user_service.get_user(user_id) is None:
            user_service.create_blank_user(user_id, status=UserStatus.ACTIVE)
        return render_template("form.html", user_id=user_id)

    @pages_bp.post("/form/<user_id>/complete")
    def complete_form(user_id):
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        email = data.get("email")
        email_hash = data.get("email_hash")
        phone = data.get("phone")

        if not name or not email or not email_hash or not phone:
            return jsonify({"error": "name, email, email_hash and phone are required"}), 400

        existing_user = user_service.find_by_email_hash(email_hash)

        if existing_user is not None and existing_user.id != user_id:
            if not existing_user.can_play():
                return jsonify({"redirect": url_for("pages.play_error_page")}), 200

            user_service.mark_play_again(existing_user)
            response = jsonify({"redirect": url_for("pages.continue_page")})
            response.set_cookie(COOKIE_NAME, existing_user.id, max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax")
            return response, 200

        try:
            user = user_service.update_user(
                user_id,
                name=name,
                email=email,
                phone=phone,
                status=UserStatus.FORM,
                email_hash=email_hash,
            )
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

        if user is None:
            return jsonify({"error": "User not found"}), 404

        response = jsonify({"redirect": url_for("pages.continue_page")})
        response.set_cookie(COOKIE_NAME, user.id, max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax")
        return response, 200

    return pages_bp
