# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.xmayriq.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

import certifi

ca = certifi.where()

client = MongoClient("mongodb+srv://minkyu:WhatIsYourTier@cluster0.1drxpub.mongodb.net/test", tlsCAFile=ca)
db = client.WhatIsYourTier

@app.route("/board", methods=["GET"])
def board():
    return render_template('board.html')

@app.route("/board/list", methods=["GET"])
def board_list():
    board_list = list(db.board.find({},{'_id':False}))
    return jsonify({'result': 'success', 'all_board': board_list})

# @app.route("/users", methods=["GET"])
# # def board_get():
#     board_list = list(db.board.find({},{'_id':False}))
#     return jsonify({'result': 'success', 'all_board': board_list})

@app.route('/GNT/write', methods=['POST'])
def board_POST():
    # board DB에 들어갈 데이터 목록 -------------------------------
    # number_receive    글번호         app.py에서 구현
    # title_receive     제목          html에서 받아옴
    # contents_receive  내용          html에서 받아옴
    # url_give
    # name_receive      이름(아이디X)   app.py에서 구현
    # date_receive      등록일         app.py에서 구현
    # ------------------------------------- ----------------

    # number_receive 구현 ------------------------------------
    board_list = list(db.board.find({}, {'_id': False}))
    count = len(board_list) + 1
    # -------------------------------------------------------

    # name_receive 구현 -------------------------------------
    # user_list = list(db.user.find({}, {'_id': False}))
    # cnt = len(user_list)
    # print('session' + session)
    # sessionID = session['id']
    # name = ''

    # for i in range(cnt):
    #     if user_list[i]['id'] == sessionID:
    #         name = user_list[i]['name']
    # ------------------------------------------------------

    # date_receive 구현 -------------------------------------
    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d %H:%M:%S')
    # ------------------------------------------------------

    # board DB에 데이터 등록 ------------------------------------
    number_receive = count
    title_receive = request.form['title_give']
    contents_receive = request.form['contents_give']
    hits = 0
    # boardurl_reveive = request.form['boardurl_give']
    # name_receive = name
    date_receive = date
    
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        user = user_info['name']
        doc = {
            'number': number_receive,
            'title': title_receive,
            'contents': contents_receive,
            # 'name': name_receive,
            'date': date_receive,
            # 'boardurl': boardurl_reveive
            'id' : user,
            'hits': hits
        }
        db.board.insert_one(doc)
        return jsonify({'msg': '등록 완료 !'})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))



# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'SPARTA'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib


#################################
##  HTML을 주는 부분             ##
#################################
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('index.html', nickname=user_info["name"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/register', methods=["GET"])
def register_get():
    return render_template('register.html')

@app.route('/post/<int:number>', methods=["GET"])
def post(number):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        hits = db.board.find_one({"number":number})['hits']
        db.board.update_one({"number": number},{'$set':{'hits': hits+1}})
        return render_template("post.html", num = number)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
        
@app.route('/post', methods=["GET","POST"])
def post_show():
        token_receive = request.cookies.get('mytoken')
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.user.find_one({"id": payload['id']})['id']
            number = request.form['num']
            one_post = db.board.find_one({'number': int(number)})
            user = one_post['id']
            title = one_post['title']
            contents = one_post['contents']
            return jsonify({'title': title, 'contents': contents, 'user': user})
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/GNT/modify', methods=["POST"])
def update():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})['id']

        title = request.form['title_give']
        contents = request.form['contents_give']
        number = int(request.form['num_give'])
        text = db.board.find_one({"number": number})

        id = text['id']
        db.board.update_one({"number": number},{'$set':{'title':title, 'contents':contents}})
        return jsonify({'title': title, 'contents': contents})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/modify/<int:number>', methods=["GET"])
def modify(number):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})['id']
        text = db.board.find_one({"number": int(number)})

        title = text['title']
        contents = text['contents']
        id = text['id']
        if id != db.user.find_one({"id": payload['id']})['id']:
            return render_template("board.html", num = number, msg = "본인의 글만 수정 가능합니다!")
        else:
            return render_template("modify.html", title=title, contents=contents,number=int(number))
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    

@app.route('/write', methods=["GET"])
def write_get():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('write.html', nickname=user_info["name"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    
@app.route('/search_id')
def search_id():
    return render_template('search_id.html')

@app.route('/search_pw')
def search_pw():
    return render_template('search_pw.html')
#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.



@app.route('/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    email_receive = request.form['email_give']
    name_receive = request.form['name_give']
    phone_receive = request.form['phone_give']

    if db.user.find_one({'id': id_receive}):
        return jsonify({'msg': '동일한 아이디가 존재합니다 !'})

    elif db.user.find_one({'name': name_receive}):
        return jsonify({'msg': '동일한 닉네임이 존재합니다 !'})
    elif id_receive == "":
        return jsonify({'msg': '아이디를 입력해주세요 !'})
    elif pw_receive == "":
        return jsonify({'msg': '비밀번호를 입력해주세요 !'})
    elif email_receive == "":
        return jsonify({'msg': '이메일을 입력해주세요 !'})
    elif name_receive == "":
        return jsonify({'msg': '이름을 입력해주세요 !'})
    elif phone_receive == "":
        return jsonify({'msg': '이름을 입력해주세요 !'})

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    doc = {
        'id' : id_receive,
        'pw' : pw_hash,
        'email' : email_receive,
        'name' : name_receive,
        'phone' : phone_receive
    }
    db.user.insert_one(doc)

    return jsonify({'result': 'success'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        print(token)
        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])


        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'name': userinfo['name']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

@app.route("/id_cheak", methods=["GET"]) # 아이디 중복 찾기
def id_cheak():
    user_list = list(db.user.find({}, {'_id': False}))
    return jsonify({'users': user_list})

@app.route('/change_pw', methods=['POST'])
def change_pw():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    db.user.update_one({'id': id_receive}, {'$set': {'pw': pw_hash}})
    return jsonify({'msg': '비밀번호 변경 완료'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
