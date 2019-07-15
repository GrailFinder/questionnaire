from flask import Blueprint, jsonify, request, current_app, make_response
from sqlalchemy import exc, or_
import uuid
from flask_restplus import Resource, fields, marshal_with, Namespace

from services.questmaker.api.models import User
from services.questmaker.api.utils import authenticate
from services.questmaker import db, bcrypt


api = Namespace("auth", description="register + login")

login_fields = api.model('LoginForm', {
  'email': fields.String(required=True),
  'password': fields.String(required=True),
})

register_form = api.model("RegisterForm", {
    "username": fields.String(required=True),
    "email": fields.String(required=True),
    "password": fields.String(required=True),
})

@api.route("/login")
class LoginRoute(Resource):
    @api.expect(login_fields)
    def post(self):
        """logs user in"""
        post_data = request.get_json()
        if not post_data:
            response_object = {
                'status': 'error',
                'message': 'Invalid payload.'
            }
            return make_response(jsonify(response_object), 400)
        email = post_data.get('email')
        password = post_data.get('password')

        try:
            # fetch the user data
            user = User.query.filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password, password):
                auth_token = user.encode_auth_token()
                if auth_token:
                    response_object = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode(),
                        'user_id': user.id,
                        'username': user.username,
                    }
                    return make_response(jsonify(response_object), 200)
            else:
                response_object = {
                    'status': 'error',
                    'message': 'User does not exist.'
                }
                return make_response(jsonify(response_object), 404)
        except Exception as e:
            current_app.logger.info(e)
            response_object = {
                'status': 'error',
                'message': 'Try again.'
            }
            return make_response(jsonify(response_object), 500)

    @authenticate  # you need to be logged in
    def get(self):
        """
        logs user out
        """
        response_object = {
            'status': 'success',
            'message': 'Successfully logged out.'
        }
        return jsonify(response_object), 200


@api.route("/register")
class RegisterRoute(Resource):
    @api.expect(register_form)
    def post():
        # get post data
        post_data = request.get_json()
        if not post_data:
            response_object = {
                'status': 'error',
                'message': 'Invalid payload.'
            }
            return jsonify(response_object), 400
        username = post_data.get('username')
        email = post_data.get('email')
        password = post_data.get('password')
        try:
            # check for existing user
            user = User.query.filter(
                or_(User.username == username, User.email==email)).first()
            if not user:
                # add new user to db
                new_user = User(
                    username=username,
                    email=email,
                    password=password
                )
                db.session.add(new_user)
                db.session.commit()
                # generate auth token
                auth_token = new_user.encode_auth_token()
                response_object = {
                    'status': 'success',
                    'message': 'Successfully registered.',
                    'auth_token': auth_token.decode()
                }
                return jsonify(response_object), 201
            else:
                response_object = {
                    'status': 'error',
                    'message': 'Sorry. That user already exists.'
                }
                return jsonify(response_object), 400
        # handler errors
        except (exc.IntegrityError, ValueError) as e:
            db.session.rollback()
            response_object = {
                'status': 'error',
                'message': 'Invalid payload.'
            }
            return jsonify(response_object), 400



