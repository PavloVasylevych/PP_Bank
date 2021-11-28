from flask import Flask
from User import user
from Credit import credit
from Bank import bank
app = Flask(__name__)
app.register_blueprint(user)
app.register_blueprint(credit)
app.register_blueprint(bank)

@app.route('/api/v1/hello-world-4')
def index():
    return "Hello World 4"


if __name__ == '__main__':
    #serve(app, "0.0.0.0", 8080)
    app.run()
    