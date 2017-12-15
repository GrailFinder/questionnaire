from flask import Blueprint, jsonify, request, make_response, render_template
from sqlalchemy import exc
from services.questmaker.api.models import Inquiry
from services.questmaker import db

inquiry_blueprint = Blueprint('inquiry', __name__, template_folder='./templates')


@inquiry_blueprint.route('/inquiries', methods=['POST', 'GET'])
def add_inquiry():
    
    if request.method == 'POST':

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
            inquiry = Inquiry.query.filter_by(title=title).first()
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
            db.session().rollback()
            response_object = {
                'status': 'fail',
                'message': 'Invalid payload.'
            }
            return make_response(jsonify(response_object)), 400

    elif request.method == 'GET':
        
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
    """Get single inqury details"""
    response_object = {
        'status': 'fail',
        'message': 'inqury does not exist'
    }
    try:
        inqury = Inquiry.query.filter_by(id=inquiry_id).first()
        if not inqury:
            return make_response(jsonify(response_object)), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': inqury.id,
                    'title': inqury.title,
                    'created_at': inqury.created_at,
                    'questions': ["{}:{}".format(q.id, q.title) for q in inqury.questions]
                }
            }
            return make_response(jsonify(response_object)), 200
    except ValueError:
        return make_response(jsonify(response_object)), 404