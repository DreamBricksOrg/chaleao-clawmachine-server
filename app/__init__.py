from dotenv import load_dotenv

load_dotenv()

from flask import Flask

from app.config import Config
from app.db.mongo import get_database, get_mongo_client
from app.pages.pages_controller import create_pages_blueprint
from app.qr.qr_controller import create_qr_status_blueprint, qr_bp
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

    users_bp = create_user_blueprint(user_service)
    pages_bp = create_pages_blueprint(user_service)
    qr_status_bp = create_qr_status_blueprint(user_service)
    app.register_blueprint(users_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(qr_bp)
    app.register_blueprint(qr_status_bp)

    return app
