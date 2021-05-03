"""
lists API route handlers
"""
from datetime import datetime, timedelta
from typing import Dict

from flask import Blueprint, request, abort
from jose import jwt
from webargs.flaskparser import parser

from api.schemas import login_form_data
from config import SECRET_KET, EXPIRATION_MINUTES, JWT_ALGO, ALLOWED_USERS_PASSWORDS

api = Blueprint('login', __name__)


@api.route('/login', methods=["POST"])
def login():
    form_data: Dict = parser.parse(login_form_data, request)
    username = form_data['username']
    password = form_data['password']
    if username not in ALLOWED_USERS_PASSWORDS or ALLOWED_USERS_PASSWORDS[username] != str(password):
        abort(401, 'not allowed user or wrong password')
    try:
        expiration: int = int((datetime.utcnow() + timedelta(minutes=EXPIRATION_MINUTES)).timestamp())
        access_token: str = jwt.encode({
            'username': username,
            'password': password,
            'expiration': expiration
        }, SECRET_KET, algorithm=JWT_ALGO)
        return {'access_token': access_token, 'token_type': 'bearer'}
    except Exception as exp:
        abort(401, exp)
