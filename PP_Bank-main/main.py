from datetime import timedelta
from tables import TokenBlockList, User
from session import s

from flask_bcrypt import Bcrypt, check_password_hash
from flask_jwt_extended import JWTManager, get_jwt, create_access_token

from flask import Flask, request, jsonify
from User import user
from Credit import credit
from Bank import bank

from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp

app = Flask(__name__)
app.register_blueprint(user)
app.register_blueprint(credit)
app.register_blueprint(bank)

ACCESS_EXPIRES = timedelta(hours=1)
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
bcrypt = Bcrypt(app)

jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = s.query(TokenBlockList.id).filter_by(jti=jti).first()
    return token is not None

@app.route('/auth/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return {"message": "Incorrect authorization headers"}, 401

    user = s.query(User).filter_by(username=auth.username).first()
    if not user:
        return {"message": "User with such username does not exists"}, 404

    if not check_password_hash(user.password, auth.password):
        return {"message": "Provided credentials are invalid"}, 401

    return jsonify({"token": create_access_token(identity=user.username)})


@app.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    s.add(TokenBlockList(jti=jti))
    s.commit()
    return {'message': 'Token was revoked'}, 200

@app.route('/api/v1/hello-world-4')
def index():
    return "Hello World 4"


if __name__ == '__main__':
    #serve(app, "0.0.0.0", 8080)
    app.run()
    