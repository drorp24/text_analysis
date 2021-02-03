"""
API error handlers
"""
from typing import Dict, Any

from flask import jsonify
import fnc


def _format_error(error: Any, code: int, general_message='Unknown') -> Dict:
    error_type = fnc.get('name', error, default='Not Found')
    code_ = fnc.get('code', error, default=code)
    message = error if type(error) == str else fnc.get('description', error)
    message = message if message is not None else fnc.get('message', error, default=general_message)
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
