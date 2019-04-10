from flask import Blueprint, jsonify, request, make_response, render_template
from sqlalchemy import exc
from services.questmaker.api.models import Choice
from services.questmaker import db

choices_blueprint = Blueprint('choices', __name__, template_folder='./templates')


@choices_blueprint.route('/choice', methods=['POST'])
def add_choice():
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
        choice = Choice.query.filter_by(text=text).first()
        if not choice: # if there was no such Choice in db
            db.session.add(Choice(text=text))
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': f'{text} was added!'
            }
            return make_response(jsonify(response_object)), 201
        else:
            response_object = {
                'status': 'fail',
                'message': 'That choice already exists.'
            }
            return make_response(jsonify(response_object)), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session().rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400



@choices_blueprint.route('/choice/<choice_id>', methods=['GET'])
def get_single_choice(choice_id):
    """Get single choice details"""
    response_object = {
        'status': 'fail',
        'message': 'choice does not exist'
    }
    try:
        choice = Choice.query.filter_by(id=choice_id).first()
        if not choice:
            return make_response(jsonify(response_object)), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': choice.id,
                    'text': choice.text,
                    'created_at': choice.created_at,
                }
            }
            return make_response(jsonify(response_object)), 200
    except ValueError:
        return make_response(jsonify(response_object)), 404