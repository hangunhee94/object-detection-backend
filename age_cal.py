import numpy as np
# from PIL import Image, ImageOps
# import matplotlib.pyplot as plt
from mtcnn import MTCNN
import cv2
import datetime
import time
import tensorflow as tf
from keras.models import load_model
from flask import Flask, Blueprint, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient

client = MongoClient('localhost')

db = client.db_ladder_age_pred

age_cal = Blueprint("age_cal", __name__, static_folder='static', template_folder='templates')

sex_model = load_model('all_face_sex_model.h5')
male_age_model = load_model('all_face_male_age_model.h5')
female_age_model = load_model('all_face_female_age_model.h5')
# asian_age_model = load_model('asian_age_model.h5')
# all_age_model = load_model('all_face_model.h5')


def process_and_predict(file):
    image = tf.keras.preprocessing.image.load_img(file, target_size=(200, 200))
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])        
    input_arr = input_arr.astype('float32')
    input_arr /= 255.0
    input_arr = input_arr.reshape(-1, 200, 200, 3)
    
    sex_pred = sex_model.predict(input_arr)
    if sex_pred[0][0] > 0.5:
      sex = '여자'
      age_pred = female_age_model.predict(input_arr)
      # age_pred = asian_age_model.predict(input_arr)
    #   age_pred = all_age_model.predict(input_arr)
      age_pred = float(age_pred)
    else:
      sex = '남자'
      age_pred = male_age_model.predict(input_arr)
      # age_pred = asian_age_model.predict(input_arr)
    #   age_pred = all_age_model.predict(input_arr)
      age_pred = float(age_pred)
    
    return sex, age_pred

def age_cal(img_file, filename, extension, save_to):    
    img = cv2.imread(img_file)
    detector = MTCNN()
    detections = detector.detect_faces(img)

    min_conf = 0.9
    imgNum = 0
    for det in detections:
        if det['confidence'] >= min_conf:
            x, y, w, h = det['box']
            if w >= h:         
                cropped = img[int((2*y + h - w)/2 - w/4) : int((2*y + h + w)/2 + w/4), int(x - w/4) : int(x + w + w/4)]
            else:
                cropped = img[int(y - h/4) : int(y + h + h/4), int((2*x + w - h)/2 - h/4) : int((2*x + w + h)/2 + h/4)]
        # 이미지를 저장
            cv2.imwrite(f'static/img/results/{filename}_{str(imgNum)}.{extension}', cropped)
            imgNum += 1
    ages_dict = {}
    for i in range(imgNum):
        exam_img = f'static/img/results/{filename}_{str(imgNum)}.{extension}'
        sex, age_pred = process_and_predict(exam_img)
        ages_dict[exam_img] = [sex, age_pred]
        doc = {
            'original_title' : save_to,
            'result_title': exam_img,
            'sex': sex,
            'age_pred': age_pred
        }
        db.results.insert_one(doc)
            
    return ages_dict        

@age_cal.route('/calculator')
def calculator():
    file_receive = request.files['file_give']
    extension = file_receive.filename.split('.')[-1]

    now = datetime.datetime.now()
    time_now = now.strftime('%Y-%m-%d-%H-%M-%S')
    filename = f'img_{time_now}'
    save_to = f'static/img/originals/{filename}.{extension}'
    file_receive.save(save_to)
    
    # MongoDB 저장 만들어야함
    doc = {
        'img_title': save_to
    }
    db.originals.insert_one(doc)

    time.sleep(1)

    ages_dict = age_cal(save_to, filename, extension, save_to)
    return jsonify({'result' : ages_dict}) 

