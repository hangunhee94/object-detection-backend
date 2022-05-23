from pymongo import MongoClient  # DB

SECRET_KEY = 'ladder'

def get_db():
    client = MongoClient('localhost', 27017)

    return client.ladder

def get_key():
    return SECRET_KEY
