from flask_restful import Resource, fields, marshal_with, reqparse
from flask import abort, request, current_app
from sqlalchemy import exc
from services.questmaker.api.models import Answer
from services.questmaker import db
import uuid

answ_fields = {
    "id": fields.String,
    "inq_id": fields.String,
    "quest_id": fields.String,
    "choice_id": fields.String,
    "user_id": fields.String,
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
    def get(self, inq_id):
        answers = Answer.query.filter_by(inq=inq_id).all()
        if not answers:
            return abort(404)
        return answers

    def post(self):

        """
        how to create answer?
        is there a need to check if that answer exists in any way?
        """
        # try:
        #     answer = Answer.query.filter_by()

        try:
            post_data = request.get_json()

            # user_id is not necessary
            if "user_id" not in post_data:
                post_data["user_id"] = None


            id = str(uuid.uuid1())
            current_app.logger.info(f"going to make response: {id}")
            db.session.add(Answer(id=id, choice=post_data["choice_id"],
                                question=post_data["quest_id"], inq=post_data["inq_id"],
                                user=post_data["user_id"]))

            db.session.commit()
            response_object = {
                'id': id,
                'status': 'success',
            }
            return response_object, 201

        except (exc.IntegrityError, ValueError, KeyError) as e:
            current_app.logger.info(e)
            db.session().rollback()
            response_object = {
                'status': 'fail',
                'message': 'Invalid payload.'
            }
            return 400, 400




        

