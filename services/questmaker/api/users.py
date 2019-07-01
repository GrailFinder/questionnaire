# services/questmaker/api/users.py


from flask import jsonify, request, make_response
from sqlalchemy import exc
from flask_restplus import Resource, fields, marshal_with, reqparse, Namespace
from services.questmaker.api.models import User
from services.questmaker import db
from services.questmaker.api.utils import is_valid_uuid
from services.questmaker.api.inquiry import resource_fields as inq_fields

api = Namespace("users", description="users crud")

user_fields = {
    'id': fields.String,
    'username': fields.String,
    'email': fields.String,
    'password': fields.String,
    'active': fields.String,
    'admin': fields.String,
    'created_at': fields.DateTime,
    'inquiries': fields.List(fields.Nested(inq_fields))
}

@api.route("/")
class UserListRoute(Resource):
    @marshal_with(user_fields)
    def get(self):
        return User.query.all()

    @api.response(204, "Success")
    @api.response(400, "Validation error")
    def post():
        post_data = request.get_json()
        if not post_data:
            response_object = {
                'status': 'fail',
                'message': 'Invalid payload.'
            }
            return make_response(jsonify(response_object)), 400
        username = post_data.get('username')
        email = post_data.get('email')
        password = post_data.get('password')
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                db.session.add(User(username=username, email=email, password=password))
                db.session.commit()
                response_object = {
                    'status': 'success',
                    'message': f'{email} was added!'
                }
                return make_response(jsonify(response_object)), 201
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'Sorry. That email already exists.'
                }
                return make_response(jsonify(response_object)), 400
        except (exc.IntegrityError, ValueError) as e:
            db.session().rollback()
            response_object = {
                'status': 'fail',
                'message': 'Invalid payload.'
            }
            return make_response(jsonify(response_object)), 400


@api.route("/<string:user_id>")
class UserRoute(Resource):
    @marshal_with(user_fields)
    def get(self, user_id):
        bad_resp = {
            "message": "something is wrong",
            "status": "fail",
        }
        if not is_valid_uuid(user_id):
            bad_resp["message"] = f"invalid uuid: {user_id}"
            return make_response(jsonify(bad_resp), 400)

        user = User.query.filter_by(id=user_id).first()
        if not user:
            bad_resp["message"] = f"no user with that id: {user_id}"
            return make_response(jsonify(bad_resp), 404)
        return user, 200


