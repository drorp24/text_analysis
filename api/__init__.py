"""
Blueprint for API endpoints
"""
from flask import Blueprint

api = Blueprint('api', __name__)

# API files here
from . import api_doc_analysis
from . import api_lists

