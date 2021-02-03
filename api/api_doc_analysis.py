"""
doc_analysis API route handlers
"""
import json
from flask import jsonify, abort
import logging
from webargs.flaskparser import use_args
from . import api
from service import db
from .schemas import doc_analysis_schema


@api.route('/document/analysis/<doc_id>/')
@use_args(doc_analysis_schema, location="view_args")
def doc_analysis(args, **kwargs):
    doc_id = kwargs['doc_id']
    document = db.select_where_col(table="documents", col="id", value=doc_id)
    if document is None:
        abort(404, f"document with id = '{doc_id}' not found")
    entities = db.select_where_col(table="entities", col="doc_id", value=doc_id)
    relations = db.select_where_col(table="relations", col="doc_id", value=doc_id)
    for entity in entities:
        entity['geolocation'] = json.loads(entity['geolocation'])
    return jsonify({
        'doc_id': doc_id,
        'text': document['text'],
        'entities': entities,
        'relations': relations
    })
