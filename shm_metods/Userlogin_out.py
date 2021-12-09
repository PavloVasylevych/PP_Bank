from shm_metods.session import s
from flask_bcrypt import check_password_hash
from flask_jwt_extended import get_jwt, create_access_token
from datetime import datetime, timezone
from flask_jwt_extended import jwt_required, get_jwt
from flask import request, Blueprint, jsonify
from shm_metods.tables import User, Session, TokenBlockList

userlogin_out = Blueprint("userlogin_out", __name__)


@userlogin_out.route('/auth/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return {"message": "Incorrect authorization headers"}, 401

    user = s.query(User).filter_by(username=auth["username"]).first()
    if not user:
        return {"message": "User with such username does not exists"}, 404

    if not check_password_hash(user.password, auth.password):
        return {"message": "Provided credentials are invalid"}, 401

    return jsonify({"token": create_access_token(identity=user["username"])})


@userlogin_out.route('/auth/logout', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    s.add(TokenBlockList(jti=jti))
    s.commit()
    return {'message': 'Token was revoked'}, 200