from flask import request, Blueprint
from project import mongo

result_blueprint = Blueprint('result', __name__)


@result_blueprint.route("/results", methods=['POST', 'GET'])
def results():
    if request.method == "POST":
        post_data = request.get_json()
        mongo.db.insert(post_data)
        return post_data

    else:
        return "hello there"