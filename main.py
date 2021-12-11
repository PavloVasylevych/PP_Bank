from datetime import timedelta
from shm_metods.tables import TokenBlockList, User
from shm_metods.session import s
from flask_jwt import jwt_required
from flask_bcrypt import Bcrypt, check_password_hash
from flask_jwt_extended import JWTManager, get_jwt, create_access_token
from flask import Flask, request, jsonify
from shm_metods.User import user
from shm_metods.Credit import credit
from shm_metods.Bank import bank
from shm_metods.Userlogin_out import userlogin_out

app = Flask(__name__)
app.register_blueprint(user)
app.register_blueprint(credit)
app.register_blueprint(bank)
app.register_blueprint(userlogin_out)


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


@app.route('/api/v1/hello-world-4')
def index():
    return "Hello World 4"


if __name__ == '__main__':
    #serve(app, "0.0.0.0", 8080)
    app.run()
    