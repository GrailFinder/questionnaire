from flask import Flask
#from pymongo import MongoClient, PyMongo
from flask_pymongo import PyMongo
import os


# instantiate the db
# client = MongoClient('mongo', 27017)
# db = client.tododb
mongo = PyMongo()

def create_app():

    # init app
    app = Flask(__name__)
    # set config
    #app_settings = os.getenv('APP_SETTINGS')
    #app.config.from_object(app_settings)

    mongo.init_app(app)
   

    # register blueprint
    from project.api.result import result_blueprint
    app.register_blueprint(result_blueprint)

    return app

