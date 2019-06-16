from flask import Blueprint, jsonify, request, make_response, render_template
from sqlalchemy import exc
from services.questmaker.api.models import Question, Inquiry
from services.questmaker.api.utils import authenticate
from services.questmaker import db
from flask_restful import Resource, fields, marshal_with, reqparse

questions_blueprint = Blueprint('questions', __name__, template_folder='./templates')

@questions_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@questions_blueprint.route('/quest', methods=['POST'])
@authenticate
def add_question(resp):
    # get data from request
    post_data = request.get_json()
    print(post_data)
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400

    title = post_data.get('title')
    multichoice = post_data.get('multichoice')
    inq_id = post_data.get('inq_id')

    try:
        question = Question.query.filter_by(title=title).first()
        if not question: # if there was no such question in db
            quest = Question(title=title, multichoice=multichoice)
            if inq_id:
                # get the inq object
                inq = Inquiry.query.filter_by(id=inq_id).first()
                inq.questions.append(quest)

            db.session.add(quest)
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
    data_list = [{'id': q.id, 'title': q.title, 'created_at': q.created_at, 'multichoice': q.multichoice,
     'choices': [a.text for a in q.choices]} for q in questions]

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
                    'choices': ["{}:{}".format(a.id, a.text) for a in quest.choices]
                }
            }
            return make_response(jsonify(response_object)), 200
    except ValueError:
        return make_response(jsonify(response_object)), 404

class QuestionRoute(Resource):
    @authenticate
    def delete(self, resp, quest_id):
        # TODO add exception and stuff
        Question.query.delete(id=quest_id)
        return None, 200

    @authenticate
    def put(self, resp, quest_id):
        put_data = request.get_json()
        if "title" not in put_data or "multichoice" not in put_data:
            response_object = {
                'status': 'fail',
                'message': """Invalid payload.
                            Should have at least title
                            and multichoice options;"""
            }
            return make_response(jsonify(response_object)), 400

        quest = Question.query.filter_by(id=quest_id)
        if not quest:
            quest = Question(title=put_data["title"],
                            multichoice=put_data["multichoice"])
            db.session.add(quest)
            resp_object = {
                        "id": quest_id,
                        "status": "success",
                        }
        else:
            quest.title = put_data["title"]
            quest.multichoice = put_data["multichoice"]
        db.session.commit()
        return None, 204

