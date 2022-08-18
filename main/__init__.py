from datetime import timedelta
import datetime
from functools import wraps
import hashlib
import json
from unittest import result
from bson import ObjectId
from flask import Flask, abort, jsonify, request, Response, Blueprint, redirect
import requests
from flask_cors import CORS
from pymongo import MongoClient
import jwt
from PIL import Image
import base64
import os
from io import BytesIO
from audioop import findfactor

# 머신러닝 모델
from mtcnn import MTCNN
import cv2
import numpy as np
import tensorflow as tf
from keras.models import load_model
import time
import math

from . import member
from . import board
from . import age_cal


app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})

client = MongoClient('localhost', 27017)
db = client.ladder

app.register_blueprint(member.blueprint)
app.register_blueprint(board.blueprint)
app.register_blueprint(age_cal.age_cal)
