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
AUTH_HEADER_KEY = 'Authorization'


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


def decode_jwt(token: str):
    decoded_jwt: Dict = jwt.decode(token, SECRET_KET, JWT_ALGO)
    return decoded_jwt['username'], decoded_jwt['password'], decoded_jwt['expiration']


def auth():
    if AUTH_HEADER_KEY not in request.headers:
        abort(401, "authorization failure, missing 'Authorization' header")
    try:
        username, password, expiration = decode_jwt(token=request.headers[AUTH_HEADER_KEY].split(' ')[1])
        token_expiration: datetime = datetime.fromtimestamp(expiration)
    except Exception as exp:
        abort(401, 'authorization failure, jwt problem')
        return
    if token_expiration < datetime.utcnow():
        abort(403, 'authorization failure, token expired, please try re-login')
