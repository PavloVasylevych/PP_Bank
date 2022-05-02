import json
import pytest
import requests as requests
from shm_metods.session import s
from shm_metods.tables import *
from main import app

user1 = User(username="user1", ClientName="name1", firstName="name1", lastName="surname1", password="user1",
             status="user")
user2 = User(username="user2", ClientName="name2", firstName="name2", lastName="surname2", password="user2",
             status="manager")

session = s


def test_register_user():
    client = app.test_client()
    url = "http://127.0.0.1:5000/api/v1/User"

    user_data = {"username": "user8", "password": "user3", "ClientName": "name8", "firstName": "name3",
                 "lastName": "name3",
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

    non_existing_user_json = "{\n    \"username\": \"invalid\",\n   \"password\": \"user1\" \n} "

    not_matching_password_json = "{\n    \"username\": \"user1\",\n   \"password\": \"invalid\" \n} "

    headers = {
        'Content-Type': 'application/json'
    }
    resp = client.post(url, headers=headers, data=login_data_json)

    assert resp.status_code == 200

    resp = client.post(url, headers=headers, data=non_existing_user_json)

    assert resp.status_code == 404

    resp = client.post(url, headers=headers, data=not_matching_password_json)

    assert resp.status_code == 406


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


@pytest.fixture(scope="module")
def get_access_token_user_manager():
    client = app.test_client()
    headers = {
        'Content-Type': 'application/json'
    }

    user1_login_data = "{\n    \"username\": " \
                       "\"user1\",\n    \"password\": \"user1\" \n} "
    user2_login_data = "{\n    \"username\": " \
                       "\"user2\",\n    \"password\": \"user2\" \n} "
    resp1 = client.post("/auth/login", headers=headers, data=user1_login_data)
    resp2 = client.post("/auth/login", headers=headers, data=user2_login_data)
    yield [json.loads(resp1.get_data(as_text=True)), json.loads(resp2.get_data(as_text=True))]


def test_user_get(get_access_token_user_manager):
    client = app.test_client()
    token1 = get_access_token_user_manager[0]['access_token']
    token2 = get_access_token_user_manager[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    user = session.query(User).filter_by(username=user1.username).first()
    url = "http://127.0.0.1:5000/api/v1/User/" + str(user.id)
    invalid_url = "http://127.0.0.1:5000/api/v1/User/10000"
    resp = client.get(url, headers=headers)
    assert resp.status_code == 200
    resp = client.get(invalid_url, headers=headers)
    assert resp.status_code == 404
    resp = client.get(url, headers=invalid_headers)
    assert resp.status_code == 403


def test_user_update(get_access_token_user_manager):
    client = app.test_client()
    token1 = get_access_token_user_manager[0]['access_token']
    token2 = get_access_token_user_manager[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    json_update_user = "{\n    \"ClientName\" : \"new_name1\",\n    \"firstName\": \"new_surname1\"," \
                       "\n    \"username\": " \
                       "\"user1\" \n  } "
    invalid_json_update_user = "{\n    \"name\" : \"new_name1\",\n    \"surname\": \"new_surname1\"," \
                               "\n    \"username\": " \
                               "\"user2\" \n } "
    url = "http://127.0.0.1:5000/api/v1/User/1"
    invalid_url = "http://127.0.0.1:5000/api/v1/User/10000"
    resp = client.put(invalid_url, headers=headers, data=json_update_user)
    assert resp.status_code == 404
    resp = client.put(url, headers=invalid_headers, data=json_update_user)
    assert resp.status_code == 403
    resp = client.put(url, headers=headers, data=invalid_json_update_user)
    assert resp.status_code == 400
    resp = client.put(url, headers=headers, data=json_update_user)
    assert resp.status_code == 200





def test_bank_get(get_access_token_user_manager):
    client = app.test_client()
    token1 = get_access_token_user_manager[0]['access_token']
    token2 = get_access_token_user_manager[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    bank = session.query(Bank).filter(Bank.name != "None").first()
    url = "http://127.0.0.1:5000/api/v1/bank/" + str(bank.name)
    invalid_url = "http://127.0.0.1:5000/api/v1/bank/NonePrivat"
    resp = client.get(url, headers=headers)
    assert resp.status_code == 200
    resp = client.get(invalid_url, headers=headers)
    assert resp.status_code == 404
    resp = client.get(url, headers=invalid_headers)
    assert resp.status_code == 403


def test_bank_update(get_access_token_user_manager):
    client = app.test_client()
    token1 = get_access_token_user_manager[0]['access_token']
    token2 = get_access_token_user_manager[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    json_update_bank = "{\n    \"name\" : \"Privat24\" \n} "
    invalid_json_update_bank = "{\n    \"name\" : \"new_name1\",\n    \"surname\": \"new_surname1\"," \
                               "\n    \"username\": " "\"user2\" \n } "
    bank = session.query(Bank).filter(Bank.name != "None").first()
    url = "http://127.0.0.1:5000/api/v1/bank/" + str(bank.name)
    invalid_url = "http://127.0.0.1:5000/api/v1/bank/NonePrivat"
    resp = client.put(invalid_url, headers=headers, data=json_update_bank)
    assert resp.status_code == 404
    resp = client.put(url, headers=invalid_headers, data=json_update_bank)
    assert resp.status_code == 403
    resp = client.put(url, headers=headers, data=invalid_json_update_bank)
    assert resp.status_code == 400
    resp = client.put(url, headers=headers, data=json_update_bank)
    assert resp.status_code == 200


def test_credit_get_all_credit(get_access_token_user_manager):
    client = app.test_client()
    token1 = get_access_token_user_manager[0]['access_token']
    token2 = get_access_token_user_manager[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    url = "http://127.0.0.1:5000/api/v1/allcredit"
    resp = client.get(url, headers=invalid_headers)
    assert resp.status_code == 403
    resp = client.get(url, headers=headers)
    assert resp.status_code == 200

def test_credit_get_all_(get_access_token_user_manager):
    client = app.test_client()
    token1 = get_access_token_user_manager[0]['access_token']
    token2 = get_access_token_user_manager[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    url = "http://127.0.0.1:5000/api/v1/alluser"
    resp = client.get(url, headers=invalid_headers)
    assert resp.status_code == 403
    resp = client.get(url, headers=headers)
    assert resp.status_code == 200


def test_credit_create(get_access_token_user_manager):
    client = app.test_client()
    token1 = get_access_token_user_manager[0]['access_token']
    token2 = get_access_token_user_manager[1]['access_token']

    credit_data = {"id_borrower": 1, "id_bank": 1, "loan_status": 0, "loan_date": "2021-11-12", "loan_amount": 10000, "interest_rate": 10}
    credit_data2 = {"username": "user7", "password": "user3", "ClientName": "name8", "firstName": "name3",
                  "lastName": "name3", "status": "user"}
    credit_data3 = {"id_borrower": 10, "id_bank": 1, "loan_status": 0, "loan_date": "2021-11-12", "loan_amount": 10000,
                   "interest_rate": 10}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    headers2 = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    url = "http://127.0.0.1:5000/api/v1/Credit"
    resp = client.post(url, headers=headers, data=json.dumps(credit_data))
    assert resp.status_code == 200
    resp = client.post(url, headers=headers, data=json.dumps(credit_data2))
    assert resp.status_code == 400
    resp = client.post(url, headers=headers, data=json.dumps(credit_data3))
    assert resp.status_code == 404
    resp = client.post(url, headers=headers2, data=json.dumps(credit_data))
    assert resp.status_code == 403


def test_credit_update(get_access_token_user_manager):
    client = app.test_client()
    token1 = get_access_token_user_manager[0]['access_token']
    token2 = get_access_token_user_manager[1]['access_token']

    credit_data = {"id_borrower": 1, "id_bank": 1, "loan_status": 0, "loan_date": "2021-11-12", "loan_amount": 10000,
                   "interest_rate": 10}
    credit_data2 = {"username": "user7", "password": "user3", "ClientName": "name8", "firstName": "name3",
                    "lastName": "name3", "status": "user"}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    headers2 = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    credit = session.query(Credit).filter(Credit.loan_status != 1).first()
    url = "http://127.0.0.1:5000/api/v1/CreditRepayment/" + str(credit.id)
    invalid_url = "http://127.0.0.1:5000/api/v1/CreditRepayment/1000"
    resp = client.put(url, headers=headers2, data=json.dumps(credit_data2))
    assert resp.status_code == 400
    resp = client.put(url, headers=headers, data=json.dumps(credit_data))
    assert resp.status_code == 403
    resp = client.put(invalid_url, headers=headers2, data=json.dumps(credit_data))
    assert resp.status_code == 404
    resp = client.put(url, headers=headers2, data=json.dumps(credit_data))
    assert resp.status_code == 200


def test_credit_delete(get_access_token_user_manager):
    client = app.test_client()
    token1 = get_access_token_user_manager[0]['access_token']
    token2 = get_access_token_user_manager[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    credit = session.query(Credit).filter(Credit.loan_status != 1).first()
    url = "http://127.0.0.1:5000/api/v1/credit/" + str(credit.id)
    invalid_url = "http://127.0.0.1:5000/api/v1/credit/10000"
    resp = client.delete(url, headers=invalid_headers)
    assert resp.status_code == 403
    resp = client.delete(invalid_url, headers=headers)
    assert resp.status_code == 404
    resp = client.delete(url, headers=headers)
    assert resp.status_code == 200



