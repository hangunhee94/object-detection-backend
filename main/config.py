from main import *
from flask import Blueprint
from pymongo import MongoClient  # DB

def get_db():
    client = MongoClient('localhost', 27017)
    return client.ladder

def get_key():
    return SECRET_KEY

def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'Authorization' in request.headers:
            abort(401)
        token = request.headers['Authorization']
        try:
            user = jwt.decode(token, SECRET_KEY, algorithms=[
                              'HS256'])
        except:
            abort(401)
        return f(user, *args, **kwargs)
    return decorated_function
