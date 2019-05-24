from flask_restful import Resource, fields, marshal_with, reqparse
from flask import abort, request, current_app, jsonify
from sqlalchemy import exc
from services.questmaker.api.models import Answer
from services.questmaker import db
import uuid

answ_fields = {
    "id": fields.String,
    "inq": fields.String,
    "question": fields.String,
    "choice": fields.String,
    "user": fields.String,
}

class AnswerRoute(Resource):
    """
    Answer to the question;
    YAGNI deleting and editing created answers
    """
    @marshal_with(answ_fields)
    def get(self, id):
        answer = Answer.query.filter_by(id=id).first()
        if not answer:
            return abort(404)
        return answer

    # def delete(self, id):
    #     """does it need to exist?"""
    #     Answer.query.filter_by(id=id).delete()

class AnswerListRoute(Resource):
    @marshal_with(answ_fields)
    def get(self):
        args = request.args
        current_app.logger.info(args)
        inq_id = args["inq_id"]
        if not inq_id:
            return abort(404)
        answers = Answer.query.filter_by(inq=inq_id).all()
        current_app.logger.info(answers)
        #if not answers:
         #   return abort(404)
        current_app.logger.info([answer.__dict__ for answer in answers])
        return [answer.__dict__ for answer in answers]

    def post(self):

        """
        how to create answer?
        is there a need to check if that answer exists in any way?
        """
        # try:
        #     answer = Answer.query.filter_by()

        try:
            post_data = request.get_json()

            # post data should be list of dicts
            assert type(post_data) is list

            current_app.logger.info(post_data)

            resp_ids = []

            for data in post_data:

                # user_id is not necessary
                if "user_id" not in data:
                    data["user_id"] = None


                id = str(uuid.uuid1())
                current_app.logger.info(f"going to make response: {id}")
                db.session.add(Answer(id=id, choice=data["choice_id"],
                                    question=data["quest_id"], inq=data["inq_id"],
                                    user=data["user_id"]))

                db.session.commit()
                resp_ids.append(id)
                response_object = {
                    'last_id': id,
                    'status': 'success',
                }
            response_object["ids"] = resp_ids
            return response_object, 201

        except (exc.IntegrityError, ValueError, KeyError) as e:
            current_app.logger.info(e)
            db.session().rollback()
            response_object = {
                'status': 'fail',
                'message': 'Invalid payload.'
            }
            return 400, 400






