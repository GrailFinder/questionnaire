from flask import Blueprint, jsonify, request, make_response, render_template
from sqlalchemy import exc
from services.questmaker.api.models import Choice
from services.questmaker.api.utils import authenticate
from services.questmaker.api.inquiry import choice_fields
from services.questmaker import db
from flask_restplus import Resource, fields, marshal_with, reqparse, Namespace

api = Namespace("choices", description="choices crud")

@api.route("/")
class ChoicesListRoute(Resource):
    @api.response(201, "Success")
    @api.response(400, 'Validation Error')
    def post():
        # get data from request
        post_data = request.get_json()
        if not post_data:
            response_object = {
                'status': 'fail',
                'message': 'Invalid payload.'
            }
            return make_response(jsonify(response_object)), 400

        text = post_data.get('text')
        question_id = post_data.get('question_id')
        value = post_data.get('value')

        try:
            choice = Choice.query.filter_by(text=text, question_id=question_id).first()
            if not choice: # if there was no such Choice in db
                db.session.add(Choice(text=text, question_id=question_id,
                    value=value))
                db.session.commit()
                response_object = {
                    'status': 'success',
                    'message': f'{text} was added!'
                }
                return make_response(jsonify(response_object)), 201
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'That choice already exists.'
                }
                return make_response(jsonify(response_object)), 400
        except (exc.IntegrityError, ValueError) as e:
            print(e)
            db.session().rollback()
            response_object = {
                'status': 'fail',
                'message': 'Invalid payload.'
            }
            return make_response(jsonify(response_object)), 400

@api.route("/<string:choice_id>")
class ChoiceRoute(Resource):
    @marshal_with(choice_fields)
    def get(choice_id):
        """Get single choice details"""
        response_object = {
            'status': 'fail',
            'message': 'choice does not exist'
        }
        try:
            choice = Choice.query.filter_by(id=choice_id).first()
            if not choice:
                return make_response(jsonify(response_object)), 404
            return make_response(jsonify(choice)), 200
        except ValueError:
            return make_response(jsonify(response_object)), 404

    @authenticate
    @api.response(204, "Success")
    @api.response(400, 'Validation Error')
    def delete(choice_id):
        '''
        Delete a choice by id
        '''
        resp = {
                'status': 'fail',
                'id': choice_id,
                }
        try:
            Choice.query.filter_by(id=choice_id).delete()
            db.session.commit()
        except Exception as e:
            return make_response(jsonify(resp), 400)
        return "", 204

    # does it need to have put method?
