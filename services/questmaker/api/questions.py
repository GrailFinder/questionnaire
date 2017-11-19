from flask import Blueprint, jsonify, request, make_response, render_template
from services.questmaker.api.models import Question
from services.questmaker import db

questions_blueprint = Blueprint('questions', __name__, template_folder='./templates')

@questions_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })