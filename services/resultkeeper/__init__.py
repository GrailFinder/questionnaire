from flask import Flask, jsonify
from pymongo import MongoClient
import os


# instantiate the db
client = MongoClient(
    os.environ['DB_PORT_27017_TCP_ADDR'],
    27017)
db = client.tododb


def create_app():

    # init app
    app = Flask(__name__)
    # set config
    #app_settings = os.getenv('APP_SETTINGS')
    #app.config.from_object(app_settings)

    db.init_app(app)

    # register blueprint

    return app

