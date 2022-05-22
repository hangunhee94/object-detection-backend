from audioop import findfactor
from datetime import datetime
from io import BytesIO
import json
from bson import ObjectId
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from PIL import Image
import base64
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.deep_pro



app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})


@app.route('/')
# @authrize
def login_page():
    return render_template('index.html')

# 측정(임시) 하기, 결과 데이터 저장하기
@app.route('/calculate', methods=['POST'])
def calculator_temporary():
    files = request.files.to_dict() # ImmutableMultiDict을 객체로 변환
    for file in files.values():
        current_time = datetime.now() # 현재 시간
        ext = file.filename.split('.')[-1]  # 이미지 확장자 추출
        filename = f"{current_time.strftime('%Y%m%d%H%M%S')}.{ext}"

        save_to = f'static/img/result_img/{filename}'  # 경로지정
        file.save(save_to)  # 이미지 파일 저장

        input_age = int(request.form['input_age'])

        result = {
            # 'user_id': user_id,
            # 'user_nick_name': user_nick_name,
            'post_id': '',
            'result_img_name': filename,
            'input_age': input_age,
            'result_age': 10
            # 'timestamp': datetime.utcnow()   
        }
        db.results.insert_one(result)
        result["_id"] = str(result["_id"])
        return jsonify({'msg': '저장되었습니다.', "result": result})


# 결과 데이터 보내기(사용 안 함)
@app.route('/result/<filename>', methods=['GET'])
def get_result(filename):
    result = db.results.find_one({"img_name": filename})
    print(result)
    if result:
        result["_id"] = str(result["_id"])
        return jsonify({"message": "success", "result": result})
    else:
        return jsonify({"message": "fail"}), 404


# 결과 데이터 삭제하기
@app.route('/result/<result_id>', methods=['DELETE'])
def delete_result(result_id):
    result = db.results.delete_one({"_id": ObjectId(result_id)})
    
    if result.deleted_count:
        return jsonify({"message": "success"})
    else:
        return jsonify({"message": "fail"}), 403


# 게시물 저장하기
@app.route('/post', methods=['POST'])
def post_file():
# if user is not None:
    files = request.files.to_dict() # ImmutableMultiDict을 객체로 변환
    for file in files.values():
        current_time = datetime.now() # 현재 시간
        ext = file.filename.split('.')[-1]  # 이미지 확장자 추출
        filename = f"{current_time.strftime('%Y%m%d%H%M%S')}.{ext}" # 이미지 이름 설정

        save_to = f'static/img/upload_img/{filename}'  # 경로지정
        file.save(save_to)  # 이미지 파일 저장

        result_id = request.form['result_id']
        input_age = int(request.form['input_age'])

        doc = {
            # 'user_id': user_id,
            # 'user_nick_name': user_nick_name,
            'result_id': result_id,
            'img_name': filename,
            'input_age': input_age,
            # 'timestamp': datetime.utcnow()   
        }
    db.posts.insert_one(doc) # posts DB에 저장

    post = db.posts.find_one({"result_id": result_id}) # posts DB의 ObjectId 찾기
    post_id = str(post["_id"])

    db.results.update_one({"_id": ObjectId(result_id)}, { # result DB에 post_id 저장 
        "$set": {"post_id": post_id}
    })

    return jsonify({'msg': '저장되었습니다.'})


# @app.route('/posts', methods=['POST'])
# def post_file():
# # if user is not None:
#     files = request.files.to_dict() # ImmutableMultiDict을 객체로 변환
#     file_list = []
#     for file in files.values():
#         extension = file.filename.split('.')[-1]
#         format = 'JPEG' if extension.lower() == 'jpg' else extension.upper()
#         img = Image.open(file)
#         wpercent = (614/ float(img.size[0]))
#         h_size = int((float(img.size[1]) * float(wpercent)))
#         img_resize = img.resize((614, h_size))
#         buffered = BytesIO()
#         img_resize.save(buffered, format)
#         image_base64 = base64.b64encode(buffered.getvalue())
#         file_list.append(image_base64)
#     # user_id = user.get('id')
#     # user_nick_name = user.get('nick_name')
#     # content = request.form['content']
#     doc = {
#         # 'user_id': user_id,
#         # 'user_nick_name': user_nick_name,
#         'file' : file_list,
#         # 'content': content,
#         # 'timestamp': datetime.utcnow()
#     }
#     db.posts.insert_one(doc)
#     return jsonify({'msg': '저장완료!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)