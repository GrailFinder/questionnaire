from flask_restplus import Resource, fields, marshal_with, reqparse, Namespace
from flask import abort, request, current_app, jsonify
from sqlalchemy import exc, text as alchemy_text
from services.questmaker.api.models import Answer
from services.questmaker import db
from services.questmaker.api.utils import is_valid_uuid, authenticate
import uuid

api = Namespace("answers", description="answers crud")

answ_fields = {
    "id": fields.String,
    "inq": fields.String,
    "question": fields.String,
    "choice": fields.String,
    "user": fields.String,
}

answer_form = api.model("AnswerForm", {
    "inq_id": fields.String(required=True),
    "quest_id": fields.String(required=True),
    "choice_id": fields.String(required=True),
    "user_id": fields.String,
})

@api.route("/<string:answer_id>")
class AnswerRoute(Resource):
    """
    Answer to the question;
    Table that keeps ids of inquiry, question, answer and user
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

@api.route("/")
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

    @api.response(201, "Success")
    @api.response(400, "Validation error")
    @api.expect(answer_form)
    def post(self):
        """
        how to create answer?
        is there a need to check if that answer exists in any way?
        theres need to check by user id,
        same user cant answer twice one the same inq
        """
        # try:
        #     answer = Answer.query.filter_by()

        try:
            post_data = request.get_json()
            user_id = None

            # post data should be dict of dicts
            assert type(post_data) is dict
            current_app.logger.info(post_data)

            bad_resp = {
                'status': 'fail',
                'message': 'Invalid payload',
            }
            if 'answers' not in post_data or 'inq_id' not in post_data:
                return make_response(jsonify(bad_resp), 403)

            # user_id is not necessary
            if post_data.get("user_id"):
                user_id = post_data["user_id"]

                # if its known user
                answered = db.session.query(Answer).filter(
                        (Answer.user==user_id) |
                        (Answer.inq==inq_id)).count()
                if answered > 0:
                    print("answered:", answered)
                    bad_resp['message'] = f"user {user_id} already answered that inquiry {inq_id}"
                    return make_response(jsonify(bad_resp), 400)

            resp_ids = []

            for data in post_data['answers']:
                id = str(uuid.uuid1())
                db.session.add(Answer(id=id, choice=data["choice_id"],
                                question=data["quest_id"],
                                inq=post_data["inq_id"],
                                user=user_id))

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

#TODO there must be a better way
answ_view_fields = {
    "id": fields.String,
    "q_id": fields.String,
    "c_id": fields.String,
    "u_id": fields.String,
    "inq_id": fields.String,
    "c_text": fields.String,
    "q_title": fields.String,
    "username": fields.String,
    "email": fields.String,
    "created_at": fields.DateTime,
}

@api.route("/view/<string:inq_id>")
class AnswerView(Resource):
    """only get"""
    @marshal_with(answ_view_fields)
    @authenticate
    def get(self, resp, inq_id):

        # some kind of check on uuid
        if not is_valid_uuid(inq_id):
            abort(404)


        query = f"""select answers.id as id,
                    answers.question as q_id,
                    answers.choice as c_id,
                    answers.user as u_id,
                    answers.inq as inq_id,
                    answers.created_at as created_at,
                    choices.text as c_text,
                    questions.title as q_title,
                    username,
                    email
                    from answers
                    inner join questions on answers.question=questions.id
                    inner join choices on answers.choice=choices.id
                    left join users on answers.user=users.id
                    where inq_id='{inq_id}';"""

        raw_result = db.engine.execute(alchemy_text(query))
        keys = raw_result.keys()
        raw_data = raw_result.fetchall()
        data = [dict(zip(keys, row)) for row in raw_data]
        print(data)
