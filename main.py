from flask import Flask

app = Flask(__name__)


@app.route('/api/v1/hello-world-4')
def index():
    return "Hello World 4"


if __name__ == '__main__':
    #serve(app, "0.0.0.0", 8080)
    app.run()
    