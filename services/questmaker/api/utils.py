from functools import wraps

from flask import request, jsonify, current_app, make_response
import uuid, sys
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
            return make_response(jsonify(response_object)), code
        auth_token = auth_header.split(" ")[1]
        resp = User.decode_auth_token(auth_token)

        current_app.logger.info(f"resp: {resp}")
        try:
            uuid.UUID(resp).hex  # parse 'uuid' to uuid
        except ValueError as e:
            current_app.logger.info(e)
            response_object = {
                'status': 'error',
                'message': resp,
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


def row2dict(row):
    """
    https://stackoverflow.com/questions/1958219/convert-sqlalchemy-row-object-to-python-dict
    """
    d = {}
    for column in row.__table__.columns:
        print(column)
        print("------------------")
        d[column.name] = str(getattr(row, column.name))

    return d

def is_valid_uuid(str_uuid):
    try:
        uuid.UUID(str_uuid)
        return True
    except ValueError:
        return False
