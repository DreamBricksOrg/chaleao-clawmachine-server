from dotenv import load_dotenv

load_dotenv()

from flask import Flask

from app.config import Config
from app.db.mongo import get_database, get_mongo_client
from app.pages.pages_controller import pages_bp
from app.user.user_controller import create_user_blueprint
from app.user.user_repository import UserRepository
from app.user.user_service import UserService


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo_client = get_mongo_client(app.config["MONGO_URI"])
    database = get_database(mongo_client, app.config["MONGO_DB_NAME"])
    user_repository = UserRepository(database)
    user_service = UserService(user_repository)

    users_bp = create_user_blueprint(user_service)
    app.register_blueprint(users_bp)
    app.register_blueprint(pages_bp)

    return app
