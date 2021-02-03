"""
Primary Flask app
"""
import settings
import os
import waitress
from flask import Flask
from flask_cors import CORS
from api import api as api_blueprint
from server_errors import add_error_handlers


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r'/*': {'origins': '*'}})
    app.register_blueprint(api_blueprint, url_prefix='/')
    add_error_handlers(app)
    return app


if __name__ == '__main__':
    application = create_app()
    waitress.serve(app=application, host=os.getenv('HOST'), port=os.getenv('PORT'))
