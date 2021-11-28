from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import case
from tables import Session
from tables import User,Credit, Bank
from validation_schemes import CreditSchema
from User import  auth

credit = Blueprint('credit', __name__)


session = Session()


@credit.route('/api/v1/allcredit', methods=['GET'])

def get_credit():
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



@credit.route('/api/v1/alluser', methods=['GET'])

def get_user():
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
@auth.login_required
def create_credit():
    # Get data from request body
    data = request.get_json()

    # Validate input data
    try:
        CreditSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check if user exists
    #exists = session.query(Credit.id_borrower).filter_by(id_borrower=data['id_borrower']).first()
    #if not exists:
       # return Response(status=404, response='User with this id was not found')
    # Check if bank exists
   # exists = session.query(Credit.id_bank).filter_by(id_bank=data['id_bank']).first()
    #if not exists:
    #    return Response(status=404, response='Bank with this id was not found')



    # Check if bank has enough money
    #db_credit = session.query().filter_by(id=data['id']).first()
    db_balance = session.query(Bank).filter_by(bank_id=data['id_bank']).first()
    if data['loan_amount'] > db_balance.balance:
        return Response(status=505, response='too much asked')
    # Create new credit
    new_credit = Credit(id_borrower=data['id_borrower'], id_bank =data['id_bank'],loan_status=data['loan_status'], loan_date=data['loan_date'], loan_amount=data['loan_amount'], interest_rate=data['interest_rate'])
    db_balance.balance = db_balance.balance - data['loan_amount']
    # Add new credit to db
    session.add(new_credit)
    session.add(db_balance)
    session.commit()

    return Response(response='New credit was successfully created!')

# Delete credit by name

@credit.route('/api/v1/credit/<id>', methods=['DELETE'])
@auth.login_required
def delete_credit(id):
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
#@auth.login_required
def update_credit(id):
    # Get data from request body
    data = request.get_json()

    # Validate input data
    try:
        CreditSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check if credit exists
    db_credit = session.query(Credit).filter_by(id=id).first()
    if not db_credit:
        return Response(status=404, response='A credit with provided ID was not found.')



    # Change credit data
    if 'loan_amount' in data.keys():
        modifier = float(1-db_credit.interest_rate/100)
        db_credit.loan_amount = db_credit.loan_amount-(modifier*data['loan_amount'])
        db_amount = db_credit.loan_amount
    if 'id_bank' in data.keys():
        db_credit.id_bank = data['id_bank']
    #db_balance = session.query(Bank).filter_by(bank_id='id_bank').first()
    #if db_balance.balance < db_amount:
        #return Response(status=404, response='too much money.')

    # Save changes
    #session.add(db_balance)
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
