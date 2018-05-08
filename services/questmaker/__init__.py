from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restful import Api
import os


# instantiate the db
db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():

    # init app
    app = Flask(__name__)
    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    db.init_app(app)
    bcrypt.init_app(app)
    api = Api(app)

    # register blueprint
    from services.questmaker.api.questions import questions_blueprint
    from services.questmaker.api.answers import answers_blueprint
    from services.questmaker.api.inquiry import inquiry_blueprint
    from services.questmaker.api.users import users_blueprint
    from services.questmaker.api.auth import auth_blueprint

    app.register_blueprint(questions_blueprint)
    app.register_blueprint(answers_blueprint)
    app.register_blueprint(inquiry_blueprint)
    app.register_blueprint(users_blueprint)
    app.register_blueprint(auth_blueprint)

    from services.questmaker.api.inquiry import InquiryRoute, InquiryListRoute
    api.add_resource(InquiryRoute, '/iii/<inquiry_id>')
    api.add_resource(InquiryListRoute, '/inq-list/')

    return app

