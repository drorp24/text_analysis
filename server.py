"""
Primary Flask app
"""
import os

import waitress
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv(verbose=True)
from api import api as api_blueprint
from server_errors import add_error_handlers
from swagger_settings import swagger_ui_blueprint, swagger_url


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r'/*': {'origins': '*'}})
    app.register_blueprint(api_blueprint, url_prefix='/')
    app.register_blueprint(swagger_ui_blueprint, url_prefix=swagger_url)
    add_error_handlers(app)
    return app


if __name__ == '__main__':
    application = create_app()
    waitress.serve(app=application, host=os.getenv('HOST'), port=os.getenv('PORT'))
