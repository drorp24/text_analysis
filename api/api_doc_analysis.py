"""
doc_analysis API route handlers
"""
import json
from typing import Dict, Tuple, List

import fnc
from faker import Faker
from flask import jsonify, abort, Blueprint
from webargs.flaskparser import use_args

from service import db
from .schemas import doc_analysis_schema

api = Blueprint('analysis', __name__)
TEXT_LOCALIZATION = 'ar_AA'
fake: Faker = Faker(TEXT_LOCALIZATION)
fake_english = Faker()


def _normalize_entities(entities: List[Dict], entity_id_to_feedbacks: Dict[str, Dict]) -> Tuple[Dict, List[Dict]]:
    def get_geolocations_arr(entity, entity_id_to_feedbacks: Dict[str, Dict]):
        if entity['id'] not in entity_id_to_feedbacks:
            num_props: int = fake.random.randint(5, 25)
            details = {fake_english.word(): fake_english.name() for i in range(num_props)}
            fix_details = {'schema_name': fake_english.sentence(), 'table_name': fake_english.sentence()}
            details = {**details, 'headers': fix_details}
            return {
                'geometry': json.loads(entity['geolocation']),
                'properties': {
                    'entity_location_id': entity['id'],
                    'feedback': None,
                    'explain': fake.text(),
                    'details': details
                }
            }
        return {
            **fnc.omit(['username', 'type', 'entity_id', 'document_id'], entity_id_to_feedbacks[entity['id']][0]),
            **json.loads(entity['geolocation'])
        }

    if entities is None:
        return [], []
    entities_without_text_meta = fnc.compose(
        (fnc.map, lambda entity: {**fnc.omit(['offset', 'length', 'doc_id', 'geolocation'], entity),
                                  'sub_type_id': [entity['sub_type_id']],
                                  'geolocation': get_geolocations_arr(entity=entity,
                                                                      entity_id_to_feedbacks=entity_id_to_feedbacks)}),
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
    entity_id_to_feedbacks = {}
    for entity in entities:
        entity_id = entity['id']
        user_feedbacks = db.select_all_where(table_name="entity_location_feedback",
                                             conditions={'document_id': doc_id,
                                                         'entity_id': entity_id,
                                                         'username': 'user_x'})
        if user_feedbacks is None:
            continue
        # if entity_id not in entity_id_to_feedbacks:
        #     entity_id_to_feedbacks[entity_id] = []
        entity_id_to_feedbacks[entity_id] = user_feedbacks
    entities, offsets = _normalize_entities(entities=entities, entity_id_to_feedbacks=entity_id_to_feedbacks)
    relations = _normalize_relations(relations=db.select_where_col(table="relations", col="doc_id", value=doc_id))
    return jsonify({
        'doc_id': doc_id,
        'text': document['text'],
        'offsets': offsets,
        'entities': entities,
        'relations': relations
    })


@api.route('/document/exist/<doc_id>/')
@use_args(doc_analysis_schema, location="view_args")
def document_exist(args, **kwargs):
    doc_id: str = kwargs['doc_id']
    document = db.select_where_col(table="documents", col="id", value=doc_id, get_first_row=True)
    return {
        'exist': document is not None,
        'document_id': doc_id
    }
