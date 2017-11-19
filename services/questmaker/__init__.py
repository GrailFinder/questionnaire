from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os


# instantiate the db
db = SQLAlchemy()


def create_app():

    # init app
    app = Flask(__name__)
    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)
    return app

