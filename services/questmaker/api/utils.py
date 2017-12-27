from functools import wraps

from flask import request, jsonify
import uuid
from services.questmaker.api.models import User


def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response_object = {
            'status': 'error',
            'message': 'Something went wrong. Please contact us.'
        }
        code = 401
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            response_object['message'] = 'Provide a valid auth token.'
            code = 403
            return jsonify(response_object), code
        auth_token = auth_header.split(" ")[1]
        resp = User.decode_auth_token(auth_token)
        try:
            uuid.UUID(resp).hex  # parse 'uuid' to uuid
        except ValueError:
            response_object = {
                'status': 'error',
                'message': resp
            }
            return jsonify(response_object), 401
        user = User.query.filter_by(id=resp).first()
        if not user or not user.active:
            return jsonify(response_object), code
        return f(resp, *args, **kwargs)
    return decorated_function

def is_admin(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.admin
