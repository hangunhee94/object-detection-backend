########################################################################
########################################################################
# 게시판의 내용 읽기, 쓰기, 목록 확인, 수정, 삭제 등
########################################################################
########################################################################

from main import *
from flask import Blueprint

# DB 호출
from . import config


db = config.get_db()
SECRET_KEY = config.get_key()

blueprint = Blueprint("board", __name__, url_prefix='')


# 결과 데이터 삭제하기
@blueprint.route('/result/<result_id>', methods=['DELETE'])
@config.authorize
def delete_result(user, result_id):
    result = db.results.find_one(
        {"_id": ObjectId(result_id), "user_id": user['id']})
    result_img_name = result['result_title']
    os.remove(f'main/{result_img_name}')  # result 이미지 삭제

    original_img_name = result['original_title']
    os.remove(f'main/{original_img_name}')  # original 이미지 삭제

    result_del = db.results.delete_one(
        {"_id": ObjectId(result_id)})  # 저장된 결과 데이터 삭제

    if result_del.deleted_count:
        return jsonify({"message": "success"})
    else:
        return jsonify({"message": "fail"}), 403


# 게시물 저장하기
@blueprint.route('/post', methods=['POST'])
@config.authorize
def post_file(user):
    result_id = request.form['result_id']
    result = db.results.find_one({"_id": ObjectId(result_id)})

    original_id = result['original_title']
    input_age = request.form['input_age']

    doc = {
        'user_id': user['id'],
        'result_id': result_id,
        'img_name': original_id,
        'input_age': input_age,
    }
    db.originals.insert_one(doc)  # posts DB에 저장

    post = db.originals.find_one(
        {"result_id": result_id})  # posts DB의 ObjectId 찾기
    post_id = str(post["_id"])

    db.results.update_one({"_id": ObjectId(result_id)}, {  # result DB에 post_id 저장
        "$set": {"post_id": post_id}
    })

    return jsonify({'msg': '저장되었습니다.'})