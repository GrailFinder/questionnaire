from flask import Blueprint, jsonify, request, make_response, render_template
from sqlalchemy import exc
from services.questmaker.api.models import Answer
from services.questmaker import db

answers_blueprint = Blueprint('answers', __name__, template_folder='./templates')


@answers_blueprint.route('/answer', methods=['POST'])
def add_answer():
    # get data from request
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400

    text = post_data.get('text')

    try:
        answer = Answer.query.filter_by(text=text).first()
        if not answer: # if there was no such Answer in db
            db.session.add(Answer(text=text))
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': f'{text} was added!'
            }
            return make_response(jsonify(response_object)), 201
        else:
            response_object = {
                'status': 'fail',
                'message': 'That answer already exists.'
            }
            return make_response(jsonify(response_object)), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session().rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400



@answers_blueprint.route('/answer/<answer_id>', methods=['GET'])
def get_single_answer(answer_id):
    """Get single answer details"""
    response_object = {
        'status': 'fail',
        'message': 'answer does not exist'
    }
    try:
        answer = Answer.query.filter_by(id=answer_id).first()
        if not answer:
            return make_response(jsonify(response_object)), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': answer.id,
                    'text': answer.text,
                    'created_at': answer.created_at,
                }
            }
            return make_response(jsonify(response_object)), 200
    except ValueError:
        return make_response(jsonify(response_object)), 404