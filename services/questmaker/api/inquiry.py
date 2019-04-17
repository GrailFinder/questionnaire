from flask import Blueprint, jsonify, request, make_response, render_template, current_app, abort
from flask_restful import Resource, fields, marshal_with, reqparse
from sqlalchemy import exc, text
from services.questmaker.api.models import Inquiry
from services.questmaker.api.utils import authenticate
from services.questmaker import db
import os, sys, uuid
import json

inquiry_blueprint = Blueprint('inquiry', __name__, template_folder='./templates')

#config = {'AMQP_URI': 'amqp://guest:guest@{}'.format(os.environ.get('HOST_IP'))}
config = {'AMQP_URI': "pyamqp://guest:guest@rabbit"}

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

    try:
        inquiry = Inquiry.query.filter_by(title=resp).first()
        if not inquiry: # if there was no such inquiry in db
            db.session.add(Inquiry(title=title))
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': f'{title} was added!'
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

@inquiry_blueprint.route('/inquiries', methods=['GET'])
def get_inquiries():
        
    inquiry = Inquiry.query.all()
    data_list = [{'id': i.id, 'title': i.title, 'created_at': i.created_at,
    'questions': [f'{q}' for q in i.questions]} for i in inquiry]

    response_object = {
        'status': 'success',
        'data': data_list,
    }        
    return jsonify(response_object), 200

@inquiry_blueprint.route('/inquiry/<inquiry_id>', methods=['GET'])
def get_single_inquiry(inquiry_id):
    """Get single inquiry details"""
    response_object = {
        'status': 'fail',
        'message': 'inquiry does not exist'
    }
    try:
        inquiry = Inquiry.query.filter_by(id=inquiry_id).first()
        if not inquiry:
            return make_response(jsonify(response_object)), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': inquiry.id,
                    'title': inquiry.title,
                    'created_at': inquiry.created_at,
                    'questions': ["{}:{}".format(q.id, q.title) for q in inquiry.questions]
                }
            }
            return make_response(jsonify(response_object)), 200
    except ValueError:
        return make_response(jsonify(response_object)), 404


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
            query = f"""SELECT questgroup.inquiries as inq_id,
                questions.id AS q_id,
                choices.id AS c_id,
                questions.title,
                choices.text,
                questions.multichoice,
                questions.created_at
            FROM questgroup
                JOIN questions ON questions.id::text = questgroup.questions::text
                JOIN choices ON questions.id::text = choices.question_id::text
            WHERE questgroup.inquiries::text = '{inq_id}'::text;
            """


            raw_result = db.engine.execute(text(query))

            # get column names
            keys = raw_result.keys()

            # get data
            res_data = raw_result.fetchall()

            data = [dict(zip(keys, row)) for row in res_data]

            # make dict with empty lists as values
            questions = {row["title"]: dict(choice=list(), multichoice=False) for row in data}
            # fill these values with choices
            #[questions[row["title"]].append(row["text"]) for row in data]
            print(questions)
            for row in data:
                questions[row["title"]]["choice"].append(row["text"])
                questions[row["title"]]["multichoice"] = row["multichoice"]

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
    'questions': fields.List(fields.Nested(question_fields))
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
    def delete(self, inquiry_id):
        Inquiry.query.delete(id=inquiry_id)

    
class InquiryListRoute(Resource):
    @marshal_with(resourse_fields)
    def get(self):
        return Inquiry.query.all()
    
    #@marshal_with(resourse_fields)
    def post(self):
        #args = parser.parse_args()
        post_data = request.get_json()
        title = post_data.get('title')
        current_app.logger.info(f"post title: {title}")

        try:
            inquiry = Inquiry.query.filter_by(title=title).first()
            if not inquiry: # if there was no such inquiry in db
                id = str(uuid.uuid1())
                current_app.logger.info(f"going to make response: {id}")
                db.session.add(Inquiry(title=title, id=id))
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
