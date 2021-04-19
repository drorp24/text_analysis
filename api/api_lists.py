"""
lists API route handlers
"""
from flask import jsonify, Blueprint

from service import db

api = Blueprint('lists', __name__)


@api.route('/lists')
def all_lists():
    lists = db.select_all_table(table="lists")
    return jsonify(lists)
