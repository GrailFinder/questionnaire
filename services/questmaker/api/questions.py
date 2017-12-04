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

@questions_blueprint.route('/quest', methods=['POST'])
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


@questions_blueprint.route('/quest', methods=['GET'])
def show_all():
    questions = Question.query.all()
    data_list = [{'id': q.id, 'title': q.title, 'created_at': q.created_at, 'multiansw': q.multiansw,
     'answers': [a.text for a in q.answers]} for q in questions]

    response_object = {
        'status': 'success',
        'data': data_list,
    }
    
    return jsonify(response_object), 200

@questions_blueprint.route('/quest/<quest_id>', methods=['GET'])
def get_single_quest(quest_id):
    """Get single quest details"""
    response_object = {
        'status': 'fail',
        'message': 'quest does not exist'
    }
    try:
        quest = Question.query.filter_by(id=quest_id).first()
        if not quest:
            return make_response(jsonify(response_object)), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': quest.id,
                    'title': quest.title,
                    'created_at': quest.created_at,
                    'answers': ["{}:{}".format(a.id, a.text) for a in quest.answers]
                }
            }
            return make_response(jsonify(response_object)), 200
    except ValueError:
        return make_response(jsonify(response_object)), 404