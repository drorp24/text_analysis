"""
Tests for API handlers
"""
import json
import pytest
from server import create_app


@pytest.fixture(scope='module', autouse=True)
def client():
    app = create_app()
    return app.test_client()


def test_not_found(client):
    response = client.get('/notexist')
    assert response.status_code == 404
    parsed_data = json.loads(response.data)
    assert parsed_data.get('error') == 'Not Found'


def test_meaningful_error_message(client):
    response = client.get('/document/analysis/doc_x/')
    parsed_data = json.loads(response.data)
    assert len(parsed_data.get('message')) > 0 and parsed_data.get('message') != 'Unknown'


def test_document_analysis(client):
    response = client.get('/document/analysis/doc_1/')
    parsed_data = json.loads(response.data)
    assert response.status_code == 200
    assert parsed_data.get('doc_id') == "doc_1"


def test_entities_correct_offset_and_length(client):
    response = client.get('/document/analysis/doc_1/')
    parsed_data = json.loads(response.data)
    entities = parsed_data.get('entities')
    text = parsed_data.get('text')
    for entity in entities:
        assert text[entity["offset"]:entity["offset"] + entity["length"]] == entity["word"]
