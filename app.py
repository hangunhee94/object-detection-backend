from datetime import datetime, timedelta
import hashlib
import json
from bson import ObjectId
from flask import Flask, jsonify, request, Response
from flask_cors import CORS  # flask 연결
from pymongo import MongoClient  # DB
import jwt

SECRET_KEY = 'ladder'

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
client = MongoClient('localhost', 27017)
db = client.turtle


@app.route('/')
def index():
    return jsonify({'message': 'success'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5005, debug=True)
