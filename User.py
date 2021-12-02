
from flask import Blueprint, Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from tables import Session
from tables import Credit, User
from validation_schemes import UserSchema, CreditSchema

user = Blueprint('user', __name__)
bcrypt = Bcrypt()

session = Session()



# Delete user by name
@user.route('/api/v1/User/<username>', methods=['DELETE'])
@jwt_required()
def delete_user(username):

    username_from_identity = get_jwt_identity()

    # Check if user exists
    db_user = session.query(User).filter_by(username=username).first()
    if not db_user:
        return Response(status=404, response='A user with provided name was not found.')

    if username != username_from_identity:
        return {"message": "You can't delete not your user"}, 403

    # Delete user
    session.delete(db_user)
    session.commit()
    return Response(response='User was deleted.')

# Update user by username
@user.route('/api/v1/User/<username>', methods=['PUT'])
@jwt_required()
def update_user(username):

    username_from_identity = get_jwt_identity()

    if username != username_from_identity:
        return {"message": "You can't update not your information"}, 403

    # Get data from request body
    data = request.get_json()

    # Validate input data
    try:
        UserSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check if user exists
    db_user = session.query(User).filter_by(username=username).first()

    # Change user data
    if 'username' in data.keys():
        db_user.username = data['username']
    if 'ClientName' in data.keys():
        db_user.ClientName = data['ClientName']
    if 'firstName' in data.keys():
        db_user.firstName = data['firstName']
    if 'lastName' in data.keys():
        db_user.lastName = data['lastName']
    if 'status' in data.keys():
        db_user.status = data['status']
    if 'password' in data.keys():
        hashed_password = bcrypt.generate_password_hash(data['password'])
        db_user.password = hashed_password

    # Save changes
    session.commit()
    return Response(response='User info changed')


# Get user by name
@user.route('/api/v1/User/<username>', methods=['GET'])
@jwt_required()
def get_user(username):

    username_from_identity = get_jwt_identity()

    if username != username_from_identity:
        return {"message": "You can't get not your information"}, 403

    # Check if user exists
    db_user = session.query(User).filter_by(username=username).first()
    if not db_user:
        return Response(status=404, response='A user with provided name was not found.')

    # Return user data
    user_data = {'username': db_user.username, 'password': db_user.password, 'ClientName': db_user.ClientName, 'firstName': db_user.lastName, 'lastName': db_user.firstName, 'status': db_user.status}
    return jsonify({"user": user_data})


# Register new user
@user.route('/api/v1/User', methods=['POST'])
def register():
    # Get data from request body
    data = request.get_json()

    # Validate input data
    try:
        UserSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check if user already exists
    exists = session.query(User.id).filter_by(username=data['username']).first()
    if exists:
        return Response(status=400, response='User with such username already exists.')

    # Hash user's password
    hashed_password = bcrypt.generate_password_hash(data['password'])
    # Create new user
    new_user = User(username=data['username'], password=hashed_password, ClientName=data['ClientName'], firstName=data['firstName'], lastName=data['lastName'], status=data['status'])

    # Add new user to db
    session.add(new_user)
    session.commit()

    return Response(response='New user was successfully created!')

