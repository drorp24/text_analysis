from typing import List, Dict
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, Float
from geoalchemy2 import Geography
import json

# ********* CONSTANTS ****************
DIALECT = 'postgresql'
USERNAME = 'postgres'
PASSWORD = 'deri1978'
HOST = 'localhost:5432'
DATABASE = 'text_analysis'
DATA_DIR_PATH = "../data"

# ********* SqlAlchemy INIT ****************
engine = create_engine(f'{DIALECT}://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}')
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
            Column(name="geolocation", type_=Geography(srid=4326)),  # TODO geoalchemy2 type
            Column(name="offset", type_=Integer),
            Column(name="length", type_=Integer),
            Column(name="word", type_=String)
        ]
    },
    {
        "name": "relations",
        "columns": [
            Column(name="id", primary_key=True, type_=String),
            Column(ForeignKey('entities.id'), name='from_entity_id', type_=String),
            Column(ForeignKey('entities.id'), name='to_entity_id', type_=String),
            Column(name="list_item_id", type_=String)
        ]
    }
]


def drop_tables():
    metadata.drop_all(engine)
    print(f"tables {[table['name'] for table in TABLES]} dropped")


def create_table(table_definition: Dict):
    return Table(table_definition['name'], metadata,  *table_definition['columns'])


def populate_tables(tables: List[Table]):
    for table in tables:
        with engine.connect() as connection:
            table_definition = [t for t in TABLES if t["name"] == table.name][0]
            dict_items = load_json_file(table_definition=table_definition)
            connection.execute(table.insert(), dict_items)
    print(f"tables {[table['name'] for table in TABLES]} populated")


def load_json_file(table_definition: str, dir_path=DATA_DIR_PATH) -> List[Dict]:
    json_file_name = f"{table_definition['name']}.json"
    with open(f'{dir_path}/{json_file_name}') as json_file:
        data = json.load(json_file)
    return data


def create_database():
    metadata.create_all(engine)
    print(f"tables {[table['name'] for table in TABLES]} created")


def populate_database():
    # Define schema first for drop and create tasks
    tables: List[Table] = []
    for table_definition in TABLES:
        tables.append(create_table(table_definition=table_definition))
    drop_tables()
    create_database()
    populate_tables(tables=tables)
    print('database successfully created')


if __name__ == '__main__':
    populate_database()
