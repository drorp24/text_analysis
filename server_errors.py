"""
API error handlers
"""
from typing import Any, Tuple

import fnc
from flask import jsonify


def _format_error(error: Any, code: int, general_message='Unknown') -> Tuple:
    error_type = fnc.get('name', error, default='Not Found')
    code_ = fnc.get('code', error, default=code)
    desc = error
    while not isinstance(desc, str) and desc is not None:
        desc = desc if type(desc) == str else fnc.get('description', desc)
    message = desc if desc is not None else general_message
    headers = fnc.get("headers", error, default=None)
    return jsonify(dict(error=error_type, code=code_, message=message.capitalize())), headers, code_


def add_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        response, headers, code = _format_error(error=error, code=404, general_message='Not found')
        return response, code, headers

    @app.errorhandler(422)
    @app.errorhandler(400)
    def url_validation(error):
        code_ = fnc.get('code', error, default=400)
        response, headers, code = _format_error(error=error, code=code_, general_message='Bad request')
        response.status_code = code
        if headers:
            return response, code, headers
        else:
            return response, code

    @app.errorhandler(401)
    def not_authorized(error):
        response, headers, code = _format_error(error=error, code=401, general_message='Not authorized')
        return response, code, headers

    @app.errorhandler(403)
    def expired(error):
        response, headers, code = _format_error(error=error, code=403, general_message='token expired')
        return response, code, headers
