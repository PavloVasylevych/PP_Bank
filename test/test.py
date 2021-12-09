import json
import pytest
import requests as requests
from shm_metods.session import s
from shm_metods.tables import *
from main import app

user1 = User(username="user1", ClientName="name1", firstName="name1", lastName="surname1", password="user1",
             status="user")
user2 = User(username="user2", ClientName="name2", firstName="name2", lastName="surname2", password="user2",
             status="user")

def test_register_user():
    client = app.test_client()
    url = "http://127.0.0.1:5000/api/v1/User"

    # user_data_json = "{\n    \"firstName\": \"FirstName\",\n    \"lastName\": \"LastName\",\n    \"username\": " \
    #                  "\"username\",\n    \"password\": \"pass\" \n} "
    user_data = {"username": "user8", "password": "user3", "ClientName": "name8", "firstName": "name3", "lastName": "name3",
         "status": "user"}
    user_data2 = {"username": "user7", "password": "user3", "ClientName": "name8", "firstName": "name3",
                 "lastName": "name3", "status": "user"}

    headers = {
        'Content-Type': 'application/json'
    }
    resp = requests.post(url, headers=headers, data=json.dumps(user_data2))
    assert resp.status_code == 400

    resp = requests.post(url, headers=headers, data=json.dumps(user_data))
    user = s.query(User).filter_by(username="user8").first()
    assert resp.status_code == 200
    assert user.ClientName == "name8"
    s.delete(user)
    s.commit()


@pytest.fixture(scope="module")
def create_user():
    user = User(firstName="firstName", lastName="surname", username="username", password="pass")
    s.add(user)
    s.commit()
    yield
    s.delete(user)
    s.commit()


def test_login_user(create_user):
    client = app.test_client()
    url = "http://127.0.0.1:5000/auth/login"

    login_data_json = "{\n    \"username\": \"user1\",\n   \"password\": \"user1\" \n} "

    non_password = "{\n    \"username\": \"user1\" \n} "

    user_data = {"username": "nouser", "password": "user1"}

    non_existing_user_json = "{\n    \"username\": \"user01\",\n   \"password\": \"user1\" \n} "

    not_matching_password_json = "{\n    \"username\": \"user1\",\n   \"password\": \"invalid\" \n} "

    headers = {
        'Content-Type': 'application/json'
    }

    resp = client.post(url, headers=headers, data=login_data_json)
    assert resp.status_code == 200

    resp = client.post(url, headers=headers, data=non_password)

    assert resp.status_code == 401

    resp = client.post(url, headers=headers, data=not_matching_password_json)

    assert resp.status_code == 401

    resp = client.post(url, headers=headers, data=json.dumps(user_data))
    assert resp.status_code == 404



@pytest.fixture()
def login_user(create_user):
    login_data_json = "{\n    \"username\": \"user1\",\n   \"password\": \"user1\" \n} "
    test_client = app.test_client()
    url = 'http://127.0.0.1:5000/auth/login'
    headers = {
        'Content-Type': 'application/json'
    }
    resp = test_client.post(url, headers=headers, data=login_data_json)
    access_token_data_json = json.loads(resp.get_data(as_text=True))
    return access_token_data_json

def test_logout_user(login_user):
    token = login_user["access_token"]
    client = app.test_client()
    url = "http://127.0.0.1:5000/auth/logout"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    resp = client.delete(url, headers=headers)

    black_listed_token = s.query(TokenBlockList).filter_by(jti=token).first
    assert resp.status_code == 200
    assert black_listed_token

    s.query(TokenBlockList).delete()
    s.commit()


