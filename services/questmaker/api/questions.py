from flask import Blueprint, jsonify, request, make_response, render_template
from sqlalchemy import exc
from services.questmaker.api.models import Question
from services.questmaker import db

questions_blueprint = Blueprint('questions', __name__, template_folder='./templates')

@questions_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

@questions_blueprint.route('quest', methods=['POST'])
def add_question():
    # get data from request
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400

    title = post_data.get('title')

    try:
        question = Question.query.filter_by(title=title).first()
        if not question: # if there was no such question in db
            db.session.add(Question(title=title))
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': f'{title} was added!'
            }
            return make_response(jsonify(response_object)), 201
        else:
            response_object = {
                'status': 'fail',
                'message': 'That question already exists.'
            }
            return make_response(jsonify(response_object)), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session().rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400
