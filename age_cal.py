import numpy as np
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from mtcnn import MTCNN
import cv2
import hashlib
import datetime

###########################################
'''
now = datetime.datetime.now()
time_now = now.strftime('%Y-%m-%d-%H-%M-%S')
filename = f'feed-{time_now}'

#   파일 경로 설정
save_to = f'static/img/{filename}.{extension}'
#   파일을 static/img 에 저장
file_receive.save(save_to)

post_id = hashlib.sha256((payload['user_id']+time_now).encode('utf-8')).hexdigest()
'''
###################################################

agemodel = load_model('asian_age_model.h5')

def process_and_predict(file):
    im = Image.open(file)
    width, height = im.size
    if width == height:
        im = im.resize((200,200), Image.ANTIALIAS)
    else:
        if width > height:
            left = width/2 - height/2
            right = width/2 + height/2
            top = 0
            bottom = height
            im = im.crop((left,top,right,bottom))
            im = im.resize((200,200), Image.ANTIALIAS)
        else:
            left = 0
            right = width
            top = 0
            bottom = width
            im = im.crop((left,top,right,bottom))
            im = im.resize((200,200), Image.ANTIALIAS)
            
    ar = np.asarray(im)
    ar = ar.astype('float32')
    ar /= 255.0
    ar = ar.reshape(-1, 200, 200, 3)
    
    age = agemodel.predict(ar)
    
    return age


def age_cal(img_file):
    
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
            cv2.imwrite("1test" + str(imgNum) + ".png", cropped)
            imgNum += 1
    ages_dict = {}
    for i in range(imgNum):
        exam_img = img_file + str(i) + '.png'
        age = process_and_predict(exam_img)
        ages_dict[exam_img] = age
        return ages_dict
        