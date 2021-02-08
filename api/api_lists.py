"""
lists API route handlers
"""
from flask import jsonify
import logging
import fnc
from . import api
from service import db


@api.route('/lists')
def all_lists():
    lists = db.select_all_table(table="lists")
    return jsonify(lists)
