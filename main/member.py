########################################################################
########################################################################
# 회원가입, 로그인
########################################################################
########################################################################


import requests
from main import *
from flask import Blueprint

# DB 호출
# from werkzeug.local import LocalProxy
# db = LocalProxy(get_db)

from . import config

db = config.get_db()
SECRET_KEY = config.get_key()


blueprint = Blueprint("member", __name__, url_prefix='')


########################################################################
########################################################################
########################################################################
# 토근 활성화
########################################################################
########################################################################
########################################################################


# def authorize(f):
#     @wraps(f)
#     def decorated_function():
#         if not 'Authorization' in request.headers:  # headers 에서 Authorization 인증을 하고
#             abort(401)  # Authorization 으로 토큰이 오지 않았다면 에러 401
#         # Authorization 이 headers에 있다면 token 값을 꺼내온다.
#         token = request.headers['Authorization']
#         try:
#             user = jwt.decode(token, SECRET_KEY, algorithms=[
#                               'HS256'])  # 꺼내온 token 값을 디코딩해서 꺼내주고
#         except:
#             abort(401)  # 디코딩이 안될 경우 에러 401
#         return f(user)
#     return decorated_function


########################################################################
########################################################################
########################################################################
# index
########################################################################
########################################################################
########################################################################
@blueprint.route('/')
@config.authorize  # decorated 함수 적용
def index(user):
    # print(user)
    return jsonify({'message': 'success'})


########################################################################
########################################################################
########################################################################
# 회원가입
########################################################################
########################################################################
########################################################################
@blueprint.route("/signup", methods=["POST"])
def signup():
    data = json.loads(request.data)

    # DB 에 저장할 테이블 명
    user_id_receive = data["user_id"]
    email_receive = data["email"]
    password_receive = data["password"]
    password_check_receive = data["password_check"]
    user_age_receive = data["user_age"]

    # 입력 정보에 대한 에러
    try:
        if not user_id_receive or not email_receive:
            sign_error = 770
            return jsonify({'message': 'fail', 'sign_error': sign_error})
        elif '@' not in email_receive or '.' not in email_receive:
            sign_error = 771
            return jsonify({'message': 'fail', 'sign_error': sign_error})
        elif not password_receive or not password_check_receive:
            sign_error = 772
            return jsonify({'message': 'fail', 'sign_error': sign_error})
        elif password_receive != password_check_receive:
            sign_error = 773
            return jsonify({'message': 'fail', 'sign_error': sign_error})
        elif not user_age_receive:
            sign_error = 774
            return jsonify({'message': 'fail', 'sign_error': sign_error})
            # 중복 처리
        elif db.member.find_one({'user_id': user_id_receive}):
            sign_error = 775
            return jsonify({'message': 'fail', 'sign_error': sign_error})
        elif db.member.find_one({'email': email_receive}):
            sign_error = 776
            return jsonify({'message': 'fail', 'sign_error': sign_error})
    except:
        status = 200
        return jsonify({'message': 'success', 'status': status})

    password_hash = hashlib.sha256(
        data["password"].encode('utf-8')).hexdigest()

    doc = {
        'user_id': data.get('user_id'),
        'email': data.get('email'),
        'password': password_hash,
        'user_age': data.get('user_age'),
    }

    db.member.insert_one(doc)

    return jsonify({'message': 'success'})


########################################################################
########################################################################
########################################################################
# 로그인
########################################################################
########################################################################
########################################################################
@blueprint.route("/login", methods=["POST"])
def login():
    data = json.loads(request.data)
    # print(data)

    user_id = data.get("user_id")
    password = data.get("password")
    hashed_pw = hashlib.sha256(password.encode('utf-8')).hexdigest()  # 복호화
    # print(hashed_pw)

    # 아이디 비밀번호 검사
    result = db.member.find_one({
        "user_id": user_id,
        "password": hashed_pw,
    })
    # print(result)

    if result is None:
        return jsonify({'message': 'fail'}), 401

    # 토큰 정의
    payload = {
        'id': str(result['_id']),
        'exp': datetime.datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 토큰 시간 적용
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    # print(token)

    return jsonify({'message': 'success', 'token': token})


########################################################################
########################################################################
########################################################################
# userinfo
########################################################################
########################################################################
########################################################################
@blueprint.route("/getuserinfo", methods=["GET"])
@config.authorize
def get_user_info(user):
    result = db.member.find_one({
        '_id': ObjectId(user['id'])
    })

    # print(result)

    return jsonify({'message': 'success', 'email': result['user_id']})

########################################################################
########################################################################
########################################################################
# kakao_login
########################################################################
########################################################################
########################################################################


@blueprint.route('/oauth',  methods=["POST"])
def oauth():
    data = json.loads(request.data)
    # code = str(request.args.get('code'))
    code = data.get("code")
    # XXXXXXXXX 자리에 RESET API KEY값을 사용
    resToken = getAccessToken("0e70ecca261b084cdb1cb36a41645ec2", str(code))
    print(resToken)
    profile = kakaoprofile(resToken['access_token'])

    print(profile['kakao_account']['email'])
    print(profile['id'])

    email = profile['kakao_account']['email']
    id = profile['id']

    user = db.member.find_one({'email': email})

    if user is None:
        db.member.insert_one({'email': email, 'user_id': id})

    result = db.member.find_one({
        "email": email,
        "user_id": id,
    })
    if result is None:
        return jsonify({'message': 'fail'}), 401
    payload = {
        'id': str(result['_id']),
        'exp': datetime.datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 토큰 시간 적용
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    # url = "http: // localhost: 5500/templates/post.html"
    return jsonify({'message': 'success', 'token': token, 'id': id, 'email': email, 'code': code})

    # return jsonify({'message': 'code=' + str(code) + '<br/>response for token=' + str(resToken) + '<br/>profile=' + str(profile)})


def getAccessToken(clientId, code):  # 세션 코드값 code 를 이용해서 ACESS TOKEN과 REFRESH TOKEN을 발급 받음
    url = "https://kauth.kakao.com/oauth/token"
    payload = "grant_type=authorization_code"
    payload += "&client_id=" + clientId
    payload += "&redirect_url=http%3A%2F%2Flocalhost%3A5005%2Foauth&code=" + code
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
    }
    reponse = requests.request("POST", url, data=payload, headers=headers)
    access_token = json.loads(((reponse.text).encode('utf-8')))
    return access_token

##kakao profile-list##


def kakaoprofile(accessToken):
    url = "https://kapi.kakao.com/v2/user/me"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        'Authorization': "Bearer " + accessToken,
    }
    response = requests.request("GET", url, headers=headers)
    access_token = json.loads(((response.text).encode('utf-8')))

    return access_token
