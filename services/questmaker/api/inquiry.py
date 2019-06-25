from flask import Blueprint, jsonify, request, make_response, render_template, current_app, abort
from flask_restful import Resource, fields, marshal_with, reqparse
from sqlalchemy import exc, text
from services.questmaker.api.models import Inquiry, Question, Choice, Answer
from services.questmaker.api.utils import authenticate, is_valid_uuid
from services.questmaker import db
import os, sys, uuid
import json

inquiry_blueprint = Blueprint('inquiry', __name__, template_folder='./templates')


@inquiry_blueprint.route('/inquiries', methods=['POST'])
@authenticate
def add_inquiry(resp):

    # get data from request
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400

    title = post_data.get('title')
    user_id = None
    if "user_id" in post_data:
        user_id = post_data["user_id"]

    try:
        inquiry = Inquiry.query.filter_by(title=resp).first()
        if not inquiry: # if there was no such inquiry in db
            id = str(uuid.uuid1())
            db.session.add(Inquiry(title=title, user_id=user_id, id=id))
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': f'{title} was added!',
                'id': id,
            }
            return make_response(jsonify(response_object)), 201
        else:
            response_object = {
                'status': 'fail',
                'message': 'That inquiry already exists.'
            }
            return make_response(jsonify(response_object)), 400
    except (exc.IntegrityError, ValueError) as e:
        current_app.logger.info(e)
        db.session().rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400

@inquiry_blueprint.route('/inq-view/<inq_id>', methods=['GET'])
def get_inq_view(inq_id):
    """
    instead of view in postgress, make joins in this method
    all inq info in one request
    """
    response_object = {
        'status': 'fail',
        'message': 'inquiry does not exist'
    }
    try:
        inquiry = Inquiry.query.filter_by(id=inq_id).first()
        if not inquiry:
            return make_response(jsonify(response_object)), 404
        else:
            query = f"""select inquiries.id as inq_id,
		inquiries.title as inq_title,
		questions.id as q_id,
		choices.id as c_id,
                choices.text,
		questions.title as q_title,
		questions.multichoice
            from inquiries
                join questions on questions.inq_id::text = inquiries.id::text
                join choices on questions.id::text = choices.question_id::text
            WHERE inquiries.id::text = '{inq_id}'::text;
            """

            """
            result = db.session.query(Question, Choice).join(Choice,
                    Question.id == Choice.question_id)\
                .filter(Question.inq_id==inq_id).all()
            # result is a list of objects (questions, choices)
            return make_response(jsonify(result), 200)
            """


            raw_result = db.engine.execute(text(query))

            # get column names
            keys = raw_result.keys()

            # get data
            res_data = raw_result.fetchall()

            data = [dict(zip(keys, row)) for row in res_data]

            # make dict with empty lists as values
            questions = {row["q_title"]: dict(choice=dict(), multichoice=False) for row in data}
            # fill these values with choices
            #[questions[row["title"]].append(row["text"]) for row in data]
            for row in data:
                questions[row["q_title"]]["choice"][row["c_id"]] = row["text"]
                questions[row["q_title"]]["multichoice"] = row["multichoice"]
                questions[row["q_title"]]["question_id"] = row["q_id"]

            response_object = {
                'status': 'success',
                'data': questions
            }
            return make_response(jsonify(response_object)), 200
    except ValueError:
        return make_response(jsonify(response_object)), 404


@inquiry_blueprint.route('/', methods=['GET'])
def show_index():
    inquiries = Inquiry.query.all()
    return render_template('index.html', inquiries=inquiries)

@inquiry_blueprint.route('/front-inq/<inquiry_id>', methods=['GET'])
def show_inquiry(inquiry_id):
    inquiry = Inquiry.query.filter_by(id=inquiry_id).first()
    return render_template('inquiry.html', questions=inquiry.questions)



question_fields = {
    'id': fields.String,
    'title': fields.String,
    'created_at': fields.DateTime,
    'multichoice': fields.Boolean,
}

resourse_fields = {
    'id': fields.String,
    'title': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
    'description': fields.String,
    'questions': fields.List(fields.Nested(question_fields)),
    'user_id': fields.String,
    'public': fields.Boolean,
}

parser = reqparse.RequestParser()
parser.add_argument('title')

class InquiryRoute(Resource):
    @marshal_with(resourse_fields)
    def get(self, inquiry_id):
        inq = Inquiry.query.filter_by(id=inquiry_id).first()
        if not inq:
            return abort(404)
        return inq

    @authenticate
    def delete(self, resp, inquiry_id):
        resp = {
                'status': 'fail',
                'id': inquiry_id,
                }
        try:
            Inquiry.query.filter_by(id=inquiry_id).delete()
            db.session.commit()
        except Exception as e:
            return make_response(jsonify(resp), 400)
        return "", 204


class InquiryListRoute(Resource):
    @marshal_with(resourse_fields)
    def get(self):
        return Inquiry.query.all()

    # without authentication should create anon inq
    # available for everyone
    def post(self):
        #args = parser.parse_args()
        post_data = request.get_json()
        title = post_data.get('title')
        # check for other keys like user_id
        user_id = None

        # dont use user_id from front anyway
        if "user_id" in post_data:
            user_id = post_data["user_id"]

        current_app.logger.info(f"post title: {title}, user_id: {user_id}")

        try:
            inquiry = Inquiry.query.filter_by(title=title).first()
            if not inquiry: # if there was no such inquiry in db
                id = str(uuid.uuid1())
                current_app.logger.info(f"going to make response: {id}")
                db.session.add(Inquiry(title=title, id=id, user_id=user_id))
                db.session.commit()
                response_object = {
                    'id': id,
                }
                return response_object, 201
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'That inquiry already exists.'
                }
                return response_object, 400
        except (exc.IntegrityError, ValueError) as e:
            current_app.logger.info(e)
            db.session().rollback()
            response_object = {
                'status': 'fail',
                'message': 'Invalid payload.'
            }
            return 400, 400

class UserInqs(Resource):
    def get(self, user_id):
        bad_resp = {
            "status": "fail",
            "message": "something went wrong",
        }

        if not is_valid_uuid(user_id):
            return make_response(jsonify(bad_resp), 404)

        unanswered_inqs = db.session.query(Inquiry, Answer).outerjoin(Answer,
                Inquiry.id==Answer.inq).filter(
                (Answer.user!=user_id) | (Answer.user==None)
            ).all()

        unanswered_inqs = [el.serialize for tupel in unanswered_inqs
                for el in tupel if type(el) == Inquiry]
        return make_response(jsonify(unanswered_inqs), 200)


