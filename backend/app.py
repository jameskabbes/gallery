from flask import Flask, make_response
from flask_cors import CORS
from src import params

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})

app.secret_key = params.FLASK_SECRET_KEY_PATH.read_text()


@app.route('/')
def home():
    return make_response('<p>backend</p>', 200)


if __name__ == '__main__':
    app.run(**{
        "debug": True,
        "host": "0.0.0.0",
        "port": 8080
    })
