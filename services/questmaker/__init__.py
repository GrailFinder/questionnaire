from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restful import Api
import os
from flask_cors import CORS, cross_origin


# instantiate the db
db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():

    # init app
    app = Flask(__name__)

    #cors
    cors = CORS(app)
    #app.config['CORS_HEADERS'] = 'Content-Type'


    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    db.init_app(app)
    bcrypt.init_app(app)
    api = Api(app)

    # register blueprint
    from services.questmaker.api.questions import questions_blueprint
    from services.questmaker.api.choices import choices_blueprint
    from services.questmaker.api.inquiry import inquiry_blueprint
    from services.questmaker.api.users import users_blueprint
    from services.questmaker.api.auth import auth_blueprint

    app.register_blueprint(questions_blueprint)
    app.register_blueprint(choices_blueprint)
    app.register_blueprint(inquiry_blueprint)
    app.register_blueprint(users_blueprint)
    app.register_blueprint(auth_blueprint)

    from services.questmaker.api.inquiry import InquiryRoute, InquiryListRoute
    api.add_resource(InquiryRoute, '/inq/<inquiry_id>')
    api.add_resource(InquiryListRoute, '/inqs/')

    from services.questmaker.api.answers import AnswerListRoute, AnswerRoute
    api.add_resource(AnswerListRoute, '/answers')
    api.add_resource(AnswerRoute, '/answer/<id>')

    return app

