"""
doc_analysis API route handlers
"""
import json
from typing import Dict, Tuple, List

from flask import jsonify, abort
import logging
from webargs.flaskparser import use_args
from . import api
from service import db
from .schemas import doc_analysis_schema
import fnc


def _normalize_entities(entities: List[Dict]) -> Tuple[Dict, List[Dict]]:
    if entities is None:
        return [], []
    entities_without_text_meta = fnc.compose(
        (fnc.map, lambda entity: {**fnc.omit(['offset', 'length', 'doc_id'], entity),
                                  'sub_type_id': [entity['sub_type_id']],
                                  'geolocation': json.loads(entity['geolocation'])}),
        (fnc.unionby, 'id'),
        (fnc.keyby, 'id')
    )(entities)
    entities_text_meta = fnc.map(lambda entity: fnc.pick(['offset', 'length', 'id'], entity), entities)
    return entities_without_text_meta, list(entities_text_meta)


def _normalize_relations(relations: List[Dict]) -> List[Dict]:
    if relations is None:
        return []
    return list(fnc.map(lambda relation: fnc.omit(['doc_id'], relation), relations))


@api.route('/document/analysis/<doc_id>/')
@use_args(doc_analysis_schema, location="view_args")
def doc_analysis(args, **kwargs):
    doc_id = kwargs['doc_id']
    document = db.select_where_col(table="documents", col="id", value=doc_id, get_first_row=True)
    if document is None:
        abort(404, f"document with id = '{doc_id}' not found")
    entities = db.select_where_col(table="entities", col="doc_id", value=doc_id)
    entities, offsets = _normalize_entities(entities=entities)
    relations = _normalize_relations(relations=db.select_where_col(table="relations", col="doc_id", value=doc_id))
    return jsonify({
        'doc_id': doc_id,
        'text': document['text'],
        'offsets': offsets,
        'entities': entities,
        'relations': relations
    })
