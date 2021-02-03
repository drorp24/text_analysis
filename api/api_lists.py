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
    lists_dict = {}
    for list_item in lists:
        if list_item['list_name'] not in lists_dict:
            lists_dict[list_item['list_name']] = []
        lists_dict[list_item['list_name']].append(fnc.omit('list_name', list_item))
    return jsonify(lists_dict)
