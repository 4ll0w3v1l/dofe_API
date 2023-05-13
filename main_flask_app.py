import json
from datetime import datetime
from flask import Flask, request, make_response, Response
from DbOperations import DBOperation as dB
from hashlib import sha256

app = Flask(__name__)


@app.route('/account/register', methods=['POST'])
def register():
    data = request.get_json()
    print(data['email'], data['password'])
    e, p = data['email'], data['password']
    status = dB().user_registration(e, p)
    print(status)
    response = make_response()
    if status[0] == 200:
        response.headers['Response'] = status[0]
        response.status_code = status[0]
        response.set_cookie('Authorization', status[1])
        print(response)
    else:
        response.headers['Response'] = status[1]
        response.status_code = status[0]
    return response


@app.route('/account/<uid>', methods=['GET'])
def account_actions(uid):
    try:
        if int(uid) <= 0:
            return Response(status=400)
    except:
        return Response(status=400)

    cookie = request.cookies['Authorization']
    status = dB().token_valid_acc(uid, cookie)
    if status[0]:
        resp = list(dB().get_acc(uid))
        response = make_response(json.dumps({'id': resp[0], 'name': resp[1], 'email': resp[2]}))
        response.status_code = 200
        return response
    else:
        return Response(status=401)


@app.route('/account/login',  methods=['POST'])
def login():
    data = request.get_json()
    e, p = data['email'], data['password']
    status = dB().login(e, p)

    response = make_response()
    print(status)
    if status[0] == 1:
        response.status_code = 200
        response.set_cookie('Authorization', status[1])
    else:
        response.status_code = status[0]
        response.headers['Response'] = status[1]
    return response
