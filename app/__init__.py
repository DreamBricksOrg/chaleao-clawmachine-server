from dotenv import load_dotenv

load_dotenv()

from flask import Flask

from app.config import Config
from app.db.mongo import get_database, get_mongo_client
from app.decrypt.decrypt_controller import create_decrypt_blueprint
from app.docs.docs_controller import docs_bp, swagger_ui_bp
from app.pages.pages_controller import create_pages_blueprint
from app.totem.session_repository import TotemSessionRepository
from app.totem.session_service import TotemSessionService
from app.totem.totem_controller import create_totem_api_blueprint
from app.user.user_controller import create_user_blueprint
from app.user.user_repository import UserRepository
from app.user.user_service import UserService


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo_client = get_mongo_client(
        app.config["MONGO_URI"],
        username=app.config["MONGO_USER"],
        password=app.config["MONGO_PASSWORD"],
    )
    database = get_database(mongo_client, app.config["MONGO_DB_NAME"])
    user_repository = UserRepository(database)
    user_service = UserService(user_repository)
    session_repository = TotemSessionRepository(database)
    session_service = TotemSessionService(session_repository, user_service)

    users_bp = create_user_blueprint(user_service)
    pages_bp = create_pages_blueprint(session_service)
    totem_bp = create_totem_api_blueprint(session_service)
    decrypt_bp = create_decrypt_blueprint(app.config)
    app.register_blueprint(users_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(totem_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(swagger_ui_bp)
    app.register_blueprint(decrypt_bp)

    return app
