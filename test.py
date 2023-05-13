import pytest
from flask import Flask, request, make_response
from main_flask_app import login

@pytest.fixture
def client():
    app = Flask(__name__)

    @app.route('/account/login', methods=['POST'])
    def test_login():
        data = request.get_json()
        e, p = data['email'], data['password']
        status = login(e, p)

        response = make_response()
        if status[0] == 1:
            response.status_code = 200
            response.set_cookie('Authorization', status[1])
        else:
            response.status_code = status[0]
            response.headers['Response'] = status[1]
        return response

    with app.test_client() as client:
        yield client

def test_login_success(client):
    data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = client.post('http://127.0.0.1:5000/account/login', json=data)
    assert response.status_code == 200
    assert 'Authorization' in response.headers['Set-Cookie']

def test_login_failure(client):
    data = {
        'email': 'test@example.com',
        'password': 'incorrect_password'
    }
    response = client.post('http://127.0.0.1:5000/account/login', json=data)
    assert response.status_code != 200
    assert 'Response' in response.headers
