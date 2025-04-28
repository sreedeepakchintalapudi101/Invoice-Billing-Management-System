import flask
from flask import request, render_template, redirect
from flask import Flask
from flask_cors import CORS
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return {
        "flag" : True,
        "message" : "Successfully launched"
    }

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8081)