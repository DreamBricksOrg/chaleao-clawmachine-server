import os


class Config:
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "clawmachine")
    MONGO_USER = os.environ.get("MONGO_USER", "")
    MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "")
