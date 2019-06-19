from flask import jsonify, request, make_response, render_template, current_app
from sqlalchemy import exc
from services.questmaker.api.models import Question, Inquiry
from services.questmaker.api.utils import authenticate
from services.questmaker import db
from flask_restful import Resource, fields, marshal_with, reqparse


choice_fields = {
    'id': fields.String,
    'text': fields.String,
    'value': fields.String,
    'created_at': fields.DateTime,
    'question_id': fields.String,
    }

resourse_fields = {
    'id': fields.String,
    'title': fields.String,
    'created_at': fields.DateTime,
    'multichoice': fields.Boolean,
    'choices': fields.List(fields.Nested(choice_fields)),
}
class QuestionRoute(Resource):
    @authenticate
    def delete(self, resp, quest_id):
        bad_resp = {
                'status': 'fail',
            }
        try:
            Question.query.filter_by(id=quest_id).delete()
            db.session.commit()
        except Exception as e:
            current_app.logger.warning(e)
            return make_response(jsonify(bad_resp)), 400
        return "", 204

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
            # we need to use given id
            quest.id = quest_id
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

    @marshal_with(resourse_fields)
    def get(self, quest_id):
        quest = Question.query.filter_by(id=quest_id).first()
        if not quest:
            return abort(404)
        return quest

class QuestionListRoute(Resource):

    @marshal_with(resourse_fields)
    def get(self):
        return Question.query.all()

    @authenticate
    def post(self, resp):

        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        # if client gives id, back uses it
        quest_id = None

        post_data = request.get_json()
        if not post_data:
            return make_response(jsonify(response_object), 400)

        try:
            title = post_data.get('title')
            multichoice = post_data.get('multichoice')
            inq_id = post_data.get('inq_id')
            if "id" in post_data:
                quest_id = post_data["id"]
        except KeyError as e:
            current_app.logger.info(e)
            return make_response(jsonify(response_object), 400)

        try:
            question = Question.query.filter_by(title=title).first()
            if not question: # if there was no such question in db
                quest = Question(title=title,
                        multichoice=multichoice, id=quest_id)
                if inq_id:
                    # get the inq object
                    inq = Inquiry.query.filter_by(id=inq_id).first()
                    inq.questions.append(quest)

                db.session.add(quest)
                db.session.commit()
                response_object = {
                    'status': 'success',
                    'message': f'{title} was added!',
                    'id': quest.id,
                }
                return make_response(jsonify(response_object), 201)
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'That question already exists.',
                }
                resp = jsonify(response_object)
                return make_response(resp, 400)
        except (exc.IntegrityError, ValueError) as e:
            db.session().rollback()
            response_object = {
                'status': 'fail',
                'message': 'Invalid payload.'
            }
            return make_response(jsonify(response_object), 400)


