import json
import os
from typing import List, Dict, Optional

from geoalchemy2 import Geography
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, Float
# ********* CONSTANTS ****************
from sqlalchemy.engine import Engine

DIALECT = 'postgresql'
USERNAME = 'postgres'
PASSWORD = 'deri1978'
HOST = 'localhost:5432'
DATABASE = 'text_analysis'
DATA_DIR_PATH = "../data"

# ********* SqlAlchemy INIT ****************
engine: Engine = create_engine(f'{DIALECT}://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}')
metadata = MetaData()
# engine.bind = metadata

# ********* SCHEMA DEFINITION ****************
TABLES = [
    {
        "name": "lists",
        "columns": [
            Column(name="id", primary_key=True, type_=String),
            Column(name="list_name", type_=String),
            Column(name="value", type_=String, nullable=True)
        ]
    },
    {
        "name": "documents",
        "columns": [
            Column(name="id", primary_key=True, type_=String),
            Column(name="text", type_=String),
        ]
    },
    {
        "name": "entities",
        "columns": [
            Column(name="id", primary_key=True, type_=String),
            Column(ForeignKey('documents.id'), name='doc_id', type_=String),
            Column(ForeignKey('lists.id'), name="type_id", type_=String),
            Column(ForeignKey('lists.id'), name="sub_type_id", type_=String, nullable=True),
            Column(name="score", type_=Float),
            Column(name="geolocation", type_=Geography(srid=4326)),
            Column(name="offset", type_=Integer),
            Column(name="length", type_=Integer),
            Column(name="word", type_=String)
        ]
    },
    {
        "name": "relations",
        "columns": [
            Column(ForeignKey('documents.id'), name='doc_id', type_=String, primary_key=True),
            Column(ForeignKey('entities.id'), name='from_entity_id', type_=String, primary_key=True),
            Column(ForeignKey('entities.id'), name='to_entity_id', type_=String, primary_key=True),
            Column(name="list_item_id", type_=String)
        ]
    },
    {
        "name": "entity_location_feedback",
        "columns": [
            Column(name="username", type_=String),
            Column(ForeignKey('documents.id'), name='document_id', type_=String, primary_key=True),
            Column(ForeignKey('entities.id'), name='entity_id', type_=String, primary_key=True),
            Column(name='entity_location_id', type_=String, primary_key=True),
            Column(name="feedback", type_=String)
        ]
    }
]


def drop_tables():
    metadata.drop_all(engine)
    print(f"tables {[table['name'] for table in TABLES]} dropped")


def create_table(table_definition: Dict):
    if table_definition['name'] not in metadata.tables:
        return Table(table_definition['name'], metadata, *table_definition['columns'])
    return metadata.tables[table_definition['name']]


def populate_tables(tables: List[Table]):
    for table in tables:
        with engine.connect() as connection:
            table_definition = [t for t in TABLES if t["name"] == table.name][0]
            dict_items = load_json_file(table_name=table_definition['name'])
            if dict_items is not None:
                connection.execute(table.insert(), dict_items)
    print(f"tables {[table['name'] for table in TABLES]} populated")


def load_json_file(table_name: str, dir_path=DATA_DIR_PATH) -> Optional[List[Dict]]:
    full_path: str = f'{dir_path}/{table_name}.json'
    if not os.path.exists(full_path):
        return None
    with open(full_path) as json_file:
        data = json.load(json_file)
    return data


def create_database():
    metadata.create_all(engine)
    print(f"tables {[table['name'] for table in TABLES]} created")


def populate_database():
    tables: List[Table] = []
    for table_definition in TABLES:
        tables.append(create_table(table_definition=table_definition))
    drop_tables()
    create_database()
    populate_tables(tables=tables)
    print('database successfully created')


if __name__ == '__main__':
    populate_database()
