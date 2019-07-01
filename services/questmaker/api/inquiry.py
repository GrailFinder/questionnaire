from flask import Blueprint, jsonify, request, make_response, render_template, current_app, abort
from flask_restplus import Resource, fields, marshal_with, Namespace
from sqlalchemy import exc, text
from services.questmaker.api.models import Inquiry, Question, Choice, Answer
from services.questmaker.api.utils import authenticate, is_valid_uuid
from services.questmaker import db
import os, sys, uuid
import json


api = Namespace("inqs", description="inquiry related operations")

choice_fields = {
    'id': fields.String,
    'text': fields.String,
    'value': fields.String,
    'created_at': fields.DateTime,
}

question_fields = {
    'id': fields.String,
    'title': fields.String,
    'created_at': fields.DateTime,
    'multichoice': fields.Boolean,
    'choices': fields.List(fields.Nested(choice_fields)),
}

resource_fields = {
    'id': fields.String,
    'title': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
    'description': fields.String,
    'questions': fields.List(fields.Nested(question_fields)),
    'user_id': fields.String,
    'public': fields.Boolean,
}


@api.route("/<string:inquiry_id>")
@api.param("inquiry_id", "inquiry identifier")
@api.doc(params={'inquiry_id': 'An ID'})
class InquiryRoute(Resource):
    @marshal_with(resource_fields)
    def get(self, inquiry_id):
        '''
        Get an inquiry by id
        '''
        inq = Inquiry.query.filter_by(id=inquiry_id).first()
        if not inq:
            return abort(404)
        return inq

    @api.response(204, "Success")
    @api.response(400, 'Validation Error')
    @authenticate
    def delete(self, resp, inquiry_id):
        '''
        Delete an inquiry by id
        '''
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


@api.route("/")
class InquiryListRoute(Resource):
    @marshal_with(resource_fields)
    def get(self):
        '''
        List all inquiries
        '''
        return Inquiry.query.all()

    # without authentication should create anon inq
    # available for everyone
    @api.response(201, "Success")
    @api.response(400, 'Validation Error')
    #@api.expect(parser)
    def post(self):
        '''
        Create an inquiry
        '''
        post_data = request.get_json()

        if not post_data or 'title' not in post_data:
            response_object = {
                'status': 'fail',
                'message': 'Invalid payload.'
            }
            return make_response(jsonify(response_object), 400)


        title = post_data.get('title')
        user_id = post_data.get('user_id')
        description = post_data.get('description')

        current_app.logger.info(f"post title: {title}, user_id: {user_id}")

        try:
            inquiry = Inquiry.query.filter_by(title=title).first()
            if not inquiry: # if there was no such inquiry in db
                id = str(uuid.uuid1())
                current_app.logger.info(f"going to make response: {id}")
                db.session.add(Inquiry(title=title, id=id,
                    description=description, user_id=user_id))
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
            return make_response(jsonify(response_object), 400)

@api.route("/by_user/<string:user_id>")
@api.param("user_id", "user identifier")
@api.doc(params={'user_id': 'An ID of user to filter out inquiries that already has been taken'})
class UserInqs(Resource):
    def get(self, user_id):
        '''
        Get inquiries that given user did not took yet
        '''
        bad_resp = {
            "status": "fail",
            "message": "something went wrong",
        }

        if not is_valid_uuid(user_id):
            return make_response(jsonify(bad_resp), 404)

        query = db.session.query(Inquiry, Answer).outerjoin(Answer,
                Inquiry.id==Answer.inq).filter(
                (Answer.user!=user_id) | (Answer.user==None)
            )

        query = f"""select * from inquiries
            where inquiries.id not in (select inq from answers
            where answers.user = '{user_id}');"""

        unanswered_inqs = db.session.query(Inquiry).from_statement(text(
                query
            )).all()
        unanswered_inqs = [el.serialize for el in unanswered_inqs]

        '''
        unanswered_inqs = query.all()
        unanswered_inqs = [el.serialize for tupel in unanswered_inqs
                for el in tupel if type(el) == Inquiry]
        '''
        return make_response(jsonify(unanswered_inqs), 200)


