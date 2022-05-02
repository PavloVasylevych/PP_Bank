from flask import Blueprint, Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import case
from shm_metods.tables import Session
from shm_metods.tables import User, Credit, Bank
from shm_metods.validation_schemes import CreditSchema

credit = Blueprint('credit', __name__)

session = Session()


# Get all credits
@credit.route('/api/v1/allcredit', methods=['GET'])
@jwt_required()
def get_credit():
    username_from_identity = get_jwt_identity()
    user = session.query(User).filter(User.id == username_from_identity).first()
    if user.status != 'manager':
        return {"message": "You can't get access to bank info if you are not a manager"}, 403

    # Get all credit from db
    credit = session.query(Credit)

    # Return all credit
    output = []
    for a in credit:
        output.append({'id': a.id,
                       'id_borrower': a.id_borrower,
                       'id_bank': a.id_bank,
                       'loan_status': a.loan_status,
                       'loan_date': a.loan_date,
                       'loan_amount': a.loan_amount,
                       'interest_rate': a.interest_rate})
    return jsonify({"credit": output})


# Get all users
@credit.route('/api/v1/alluser', methods=['GET'])
@jwt_required()
def get_user():
    username_from_identity = get_jwt_identity()
    user = session.query(User).filter(User.id == username_from_identity).first()
    if user.status != 'manager':
        return {"message": "You can't get access to bank info if you are not a manager"}, 403

    # Get all user from db
    user = session.query(User)

    # Return all users
    output = []
    for a in user:
        output.append({'id': a.id,
                       'username': a.username,
                       'ClientName': a.ClientName,
                       'firstName': a.firstName,
                       'lastName': a.lastName,
                       'status': a.status,
                       'password': a.password})
    return jsonify({"users": output})


# Create new credit
@credit.route('/api/v1/Credit', methods=['POST'])
@jwt_required()
def create_credit():
    # Get data from request body
    data = request.get_json()

    # Validate input data
    try:
        CreditSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    username_from_identity = get_jwt_identity()
    user = session.query(User).filter(User.id == username_from_identity).first()
    # Check if user exists
    exists = session.query(User).filter_by(id=data['id_borrower']).first()
    if not exists:
        return Response(status=404, response='User with this id was not found')

    if user.id != data['id_borrower']:
        return {"message": "You can add credit only with your id"}, 403

    # # Check if bank has enough money
    # db_credit = session.query(Bank).filter_by(bank_id=data['id']).first()
    # db_balance = session.query(Bank).filter_by(bank_id=data['id_bank']).first()
    # if data['loan_amount'] > db_balance.balance:
    #     return Response(status=505, response='too much asked')
    # Create new credit
    new_credit = Credit(id_borrower=data['id_borrower'], loan_status=data['loan_status'], loan_date=data['loan_date'],
                        loan_amount=data['loan_amount'], interest_rate=data['interest_rate'])
    # db_balance.balance = db_balance.balance - data['loan_amount']

    # Add new credit to db
    session.add(new_credit)
    # session.add(db_balance)
    session.commit()

    return Response(response='New credit was successfully created!')


# Delete credit by id
@credit.route('/api/v1/credit/<id>', methods=['DELETE'])
@jwt_required()
def delete_credit(id):
    username_from_identity = get_jwt_identity()
    user = session.query(User).filter(User.id == username_from_identity).first()
    if user.status != 'manager':
        return {"message": "You can't get access to bank info if you are not a manager"}, 403

    # Check if credit exists
    db_user = session.query(Credit).filter_by(id=id).first()
    if not db_user:
        return Response(status=404, response='A credit with provided id was not found.')

    # Delete user
    session.delete(db_user)
    session.commit()
    return Response(response='credit was deleted.')


# Credit repayment

@credit.route('/api/v1/CreditRepayment/<id>', methods=['PUT'])
@jwt_required()
def update_credit(id):
    # Get data from request body
    data = request.get_json()

    # Validate input data
    try:
        CreditSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    username_from_identity = get_jwt_identity()
    user = session.query(User).filter(User.id == username_from_identity).first()
    if user.status != 'manager':
        return {"message": "You can't get access to bank info if you are not a manager"}, 403


    # Check if credit exists
    db_credit = session.query(Credit).filter_by(id=id).first()
    if not db_credit:
        return Response(status=404, response='A credit with provided ID was not found.')
    # Change credit data
    if 'loan_amount' in data.keys():
        modifier = float(1 - db_credit.interest_rate / 100)
        db_credit.loan_amount = db_credit.loan_amount - (modifier * data['loan_amount'])
        db_amount = db_credit.loan_amount
    if 'id_bank' in data.keys():
        db_credit.id_bank = data['id_bank']
    # db_balance = session.query(Bank).filter_by(bank_id='id_bank').first()
    # if db_balance.balance < db_amount:
    # return Response(status=404, response='too much money.')

    # Save changes
    # session.add(db_balance)
    session.commit()

    # Return new reservation data
    credit_data = {
        'id': db_credit.id,
        'id_borrower': db_credit.id_borrower,
        'id_bank': db_credit.id_bank,
        'loan_status': db_credit.loan_status,
        'loan_date': db_credit.loan_date,
        'loan_amount': db_credit.loan_amount,
        'interest_rate': db_credit.interest_rate
    }
    return jsonify({"credit": credit_data})
