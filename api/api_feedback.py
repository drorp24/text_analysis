from typing import Dict

import flask
from flask import Blueprint, request, abort
from webargs.flaskparser import parser

from api.api_login import auth
from api.schemas import feedback_location_request_body
from service import db

api = Blueprint('feedback', __name__)


@api.route('/feedback/location', methods=["POST"])
def feedback_location():
    auth()
    try:
        parsed_input: Dict = parser.parse(feedback_location_request_body, request)  # validate input
        db.upsert(table_name='entity_location_feedback', row_as_dict=parsed_input,
                  upsert_based_on=['document_id', 'entity_id', 'entity_location_id'])
        return flask.Response()
    except Exception as exc:
        abort(422, exc)
