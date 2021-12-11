
from flask import Blueprint, Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from shm_metods.tables import Session
from shm_metods.tables import Credit, User
from shm_metods.validation_schemes import UserSchema, CreditSchema

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
@user.route('/api/v1/User/<id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    logged_in_user_id = get_jwt_identity()
    user = session.query(User).filter(User.id == id).first()
    if not user:
        return {'message': 'No users with this id.'}, 404
    if user.id != logged_in_user_id:
        return {'message': 'Access denied'}, 403
    params = request.json
    if session.query(User).filter_by(username=params['username']).first() and user.username != params['username']:
        return {"message": "User with provided username already exists"}, 400
    for key, value in params.items():
        setattr(user, key, value)
    session.commit()
    serialized = {
        "id": user.id,
        "username": user.username
    }
    return serialized


# Get user by id
@user.route('/api/v1/User/<id>', methods=['GET'])
@jwt_required()
def get_user(id):
    logged_in_user_id = get_jwt_identity()
    user = session.query(User).filter(User.id == id).first()
    if not user:
        return {'message': 'Invalid id provided'}, 404
    if user.id != logged_in_user_id:
        return {'message': 'Access denied'}, 403
    serialized = {
        "id": user.id,
        "firstName": user.firstName,
        "lastName": user.lastName,
        "username": user.username
    }
    return jsonify(serialized), 200


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

