from webargs import fields, validate

doc_analysis_schema = {"doc_id": fields.Str()}

feedback_location_request_body = {
    'username': fields.Str(required=True),
    'document_id': fields.Str(required=True),
    'entity_id': fields.Str(required=True),
    'entity_location_id': fields.Str(required=True),
    'feedback': fields.Str(required=True, allow_none=True,
                           validate=validate.OneOf([None, 'correct', 'wrong', 'not_sure']))
}
