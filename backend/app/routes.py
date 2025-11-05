# backend/app/routes.py
from flask import Blueprint, jsonify

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/hello')
def hello():
    return jsonify({'message': 'Flask API connected!'})
