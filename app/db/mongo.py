from pymongo import MongoClient


def get_mongo_client(uri):
    return MongoClient(uri)


def get_database(client, db_name):
    return client[db_name]
