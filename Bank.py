from flask import Flask, Blueprint, Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
#from flask_bcrypt import Bcrypt
from tables import Session
from tables import Credit, User,Bank
from validation_schemes import UserSchema, CreditSchema,BalanceSchema
#from User import  auth

bank = Blueprint('bank', __name__)
#bcrypt = Bcrypt()

session = Session()

# Get bank info by name
@bank.route('/api/v1/bank/<name>', methods=['GET'])
@jwt_required()
def get_bank(name):
    # Check if user exists
    db_bank = session.query(Bank).filter_by(name=name).first()
    if not db_bank:
        return Response(status=404, response='A bank with provided name was not found.')

    username_from_identity = get_jwt_identity()
    user = session.query(User).filter_by(username=username_from_identity).first()
    if user.status != 'manager':
        return {"message": "You can't get access to bank info if you are not a manager"}, 403

    # Return user data
    bank_data = {'name': db_bank.name, 'balance': db_bank.balance}
    return jsonify({"user": bank_data})

# Update bank by name
@bank.route('/api/v1/bank/<name>', methods=['PUT'])
@jwt_required()
def update_bank(name):
    # Get data from request body
    data = request.get_json()

    username_from_identity = get_jwt_identity()
    user = session.query(User).filter_by(username=username_from_identity).first()
    if user.status != 'manager':
        return {"message": "You can't get access to bank info if you are not a manager"}, 403

    # Validate input data
    try:
        BalanceSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check if bank exists
    db_bank = session.query(Bank).filter_by(name=name).first()
    if not db_bank:
        return Response(status=404, response='A bank with provided name was not found.')
    # Change bank data
    if 'name' in data.keys():
        db_bank.name = data['name']
    if 'balance' in data.keys():
        db_bank.balance = data['balance']

    # Save changes
    session.commit()
    return Response(response='Bank info changed')
