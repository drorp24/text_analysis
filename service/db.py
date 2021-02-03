import os
from typing import Any
from sqlalchemy import create_engine, MetaData, select, Table
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_AsGeoJSON

engine = create_engine(os.getenv('DB_URL'))
my_db_meta = MetaData()
my_db_meta.reflect(bind=engine)


def _execute(query):
    with engine.connect() as connection:
        return connection.execute(query)


def _normalize_result(result):
    normalized_result = [dict(row) for row in result]
    if len(normalized_result) <= 1:
        return None if len(normalized_result) < 1 else normalized_result[0]
    return normalized_result


def select_all_table(table: str) -> Any:
    table_to_select = my_db_meta.tables[table]
    select_all_query = select([table_to_select])
    result = _execute(select_all_query)
    return _normalize_result(result=result)


def select_where_col(table: str, col: str, value: Any) -> Any:
    table_to_select: Table = my_db_meta.tables[table]
    cols = [column if type(column.type) != Geography else ST_AsGeoJSON(column).label(column.name) for column in table_to_select.c]
    query = select(cols).where(table_to_select.c[col] == value)
    result = _execute(query)
    return _normalize_result(result=result)
