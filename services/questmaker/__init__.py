from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index_page():
    return 'Questionnaire place!'

app.run()