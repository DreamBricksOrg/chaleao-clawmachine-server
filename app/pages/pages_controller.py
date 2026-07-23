from flask import Blueprint, jsonify, redirect, render_template, request, url_for

COOKIE_NAME = "user_id"
COOKIE_MAX_AGE = 60 * 60 * 12  # 12 horas


def create_pages_blueprint(session_service):
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

    @pages_bp.get("/form/<session_id>")
    def form_page(session_id):
        cookie_user_id = request.cookies.get(COOKIE_NAME)
        action, user = session_service.enter_form(session_id, cookie_user_id)

        if action == "play":
            response = redirect(url_for("pages.continue_page"))
            _set_user_cookie(response, user.id)
            return response
        if action == "blocked":
            return redirect(url_for("pages.play_error_page"))
        return render_template("form.html", user_id=session_id)

    @pages_bp.post("/form/<session_id>/complete")
    def complete_form(session_id):
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        email = data.get("email")
        email_hash = data.get("email_hash")
        phone = data.get("phone")

        if not name or not email or not email_hash or not phone:
            return jsonify({"error": "name, email, email_hash and phone are required"}), 400

        try:
            action, user = session_service.complete_form(session_id, name, email, phone, email_hash)
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

        if action == "not_found":
            return jsonify({"error": "User not found"}), 404
        if action == "blocked":
            return jsonify({"redirect": url_for("pages.play_error_page")}), 200

        response = jsonify({"redirect": url_for("pages.continue_page")})
        _set_user_cookie(response, user.id)
        return response, 200

    def _set_user_cookie(response, user_id):
        response.set_cookie(
            COOKIE_NAME, user_id, max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax"
        )

    return pages_bp
