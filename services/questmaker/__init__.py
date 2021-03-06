from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restplus import Api
import os
from flask_cors import CORS, cross_origin

# instantiate the db
db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():

    authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'authorization'
        }
    }

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
    api = Api(app, authorizations=authorizations, security='apikey')

    # register blueprint
    #from services.questmaker.api.choices import choices_blueprint
#    from services.questmaker.api.inquiry import inquiry_blueprint
#    from services.questmaker.api.users import users_blueprint
    from services.questmaker.api.auth import api as auth_ns
    api.add_namespace(auth_ns)

    #app.register_blueprint(choices_blueprint)
#    app.register_blueprint(inquiry_blueprint)
#    app.register_blueprint(users_blueprint)
    #app.register_blueprint(auth_blueprint)

    from services.questmaker.api.choices import api as c_ns

    from services.questmaker.api.inquiry import (InquiryRoute,
            InquiryListRoute, UserInqs, api as i_ns)
    #api.add_resource(InquiryRoute, '/inq/<inquiry_id>')
    #api.add_resource(InquiryListRoute, '/inqs/')
    #api.add_resource(UserInqs, '/uinqs/<user_id>')
    api.add_namespace(i_ns)

    from services.questmaker.api.answers import AnswerListRoute, AnswerRoute, api as a_ns
    #api.add_resource(AnswerListRoute, '/answers')
    #api.add_resource(AnswerRoute, '/answer/<id>')

    from services.questmaker.api.questions import (QuestionRoute,
    QuestionListRoute, api as q_ns)
    #api.add_resource(QuestionRoute, '/question/<quest_id>')
    #api.add_resource(QuestionListRoute, '/questions')
    api.add_namespace(q_ns)
    api.add_namespace(c_ns)
    api.add_namespace(a_ns)

    from services.questmaker.api.users import UserRoute, UserListRoute, api as u_ns
    #api.add_resource(UserRoute, '/user/<user_id>')
    #api.add_resource(UserListRoute, '/users')
    api.add_namespace(u_ns)


    return app

