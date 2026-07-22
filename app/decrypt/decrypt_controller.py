from flask import Blueprint, redirect, render_template, request, session, url_for

SESSION_KEY = "descrypt_authenticated"


def create_decrypt_blueprint(config):
    decrypt_bp = Blueprint("decrypt", __name__)

    @decrypt_bp.route("/descrypt", methods=["GET", "POST"])
    def descrypt_page():
        error = None

        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            if username == config["DUSER"] and password == config["DPASSWORD"]:
                session[SESSION_KEY] = True
            else:
                error = "Usuário ou senha inválidos."

        authenticated = session.get(SESSION_KEY, False)
        return render_template("descrypt.html", authenticated=authenticated, error=error)

    @decrypt_bp.get("/descrypt/logout")
    def descrypt_logout():
        session.pop(SESSION_KEY, None)
        return redirect(url_for("decrypt.descrypt_page"))

    return decrypt_bp
