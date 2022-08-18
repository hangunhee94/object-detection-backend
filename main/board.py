from main import *
from flask import Blueprint
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
    os.remove(f'main/{result_img_name}')

    original_img_name = result['original_title']
    os.remove(f'main/{original_img_name}')

    result_del = db.results.delete_one(
        {"_id": ObjectId(result_id)})

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
    db.originals.insert_one(doc)

    post = db.originals.find_one(
        {"result_id": result_id})
    post_id = str(post["_id"])

    db.results.update_one({"_id": ObjectId(result_id)}, {
        "$set": {"post_id": post_id}
    })

    return jsonify({'msg': '저장되었습니다.'})