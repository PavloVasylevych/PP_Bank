from shm_metods.User import *
from flask_bcrypt import check_password_hash
from flask_jwt_extended import get_jwt, create_access_token
from datetime import datetime, timezone
from flask_jwt_extended import jwt_required, get_jwt
from flask import request, Blueprint, jsonify
from shm_metods.tables import User,Session, TokenBlockList
from flask_restful import Resource


userlogin_out = Blueprint("userlogin_out", __name__)


@userlogin_out.route('/auth/login', methods=['POST'])
def login():
    params = request.json
    if not Session.query(User).filter_by(username=params['username']).first():
        return {"message": "User with provided username not found"}, 404
    user = User.authenticate(**params)
    if not user:
        return {'message': 'Invalid password'}, 406
    token = user.get_token()
    return {'access_token': token}


@userlogin_out.route('/auth/logout', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    session.add(TokenBlockList(jti=jti, created_at=now))
    session.commit()
    return jsonify(msg="JWT revoked")