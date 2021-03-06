from flask import jsonify, request, make_response, render_template, current_app
from sqlalchemy import exc
from services.questmaker.api.models import Question, Inquiry
from services.questmaker.api.inquiry import question_fields as resource_fields
from services.questmaker.api.utils import authenticate
from services.questmaker import db
from flask_restplus import Resource, fields, marshal_with, reqparse, Namespace

api = Namespace("quests", description="questions crud")

quest_form = api.model("QuestionForm", {
        "title": fields.String(required=True),
        "multichoice": fields.Boolean,
        "inq_id": fields.String(required=True),
    })

@api.route("/<string:quest_id>")
class QuestionRoute(Resource):

    @api.response(204, "Success")
    @api.response(400, "Validation error")
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

    @api.response(204, "Success")
    @api.response(400, "Validation error")
    @authenticate
    @api.expect(quest_form)
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
        return "", 204

    @marshal_with(resource_fields)
    def get(self, quest_id):
        quest = Question.query.filter_by(id=quest_id).first()
        if not quest:
            return abort(404)
        return quest

@api.route("/")
class QuestionListRoute(Resource):

    @marshal_with(resource_fields)
    def get(self):
        return Question.query.all()

    @authenticate
    @api.response(201, "Success")
    @api.response(400, "Validation error")
    @api.expect(quest_form)
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
                    if not inq:
                        response_object["message"] = "no such inquiry exists"
                        return make_response(jsonify(response_object), 403)
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


