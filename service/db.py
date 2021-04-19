import os
from typing import Any, List, Dict

from geoalchemy2 import Geography
from geoalchemy2.functions import ST_AsGeoJSON
from sqlalchemy import create_engine, MetaData, select, Table
from sqlalchemy.engine import Engine

engine: Engine = create_engine(os.getenv('DB_URL'))
my_db_meta = MetaData()
my_db_meta.reflect(bind=engine)


def _execute(query):
    with engine.connect() as connection:
        return connection.execute(query)


def _normalize_result(result, get_first_row: bool):
    normalized_result = [dict(row) for row in result]
    if len(normalized_result) <= 1:
        return None if len(normalized_result) < 1 else normalized_result[0] if get_first_row else normalized_result
    return normalized_result


def select_all_table(table: str) -> Any:
    table_to_select = my_db_meta.tables[table]
    select_all_query = select([table_to_select])
    result = _execute(select_all_query)
    return _normalize_result(result=result, get_first_row=False)


def select_where_col(table: str, col: str, value: Any, get_first_row=False) -> Any:
    table_to_select: Table = my_db_meta.tables[table]
    cols = [column if type(column.type) != Geography else ST_AsGeoJSON(column).label(column.name) for column in
            table_to_select.c]
    query = select(cols).where(table_to_select.c[col] == value)
    result = _execute(query)
    return _normalize_result(result=result, get_first_row=get_first_row)


def upsert(table_name: str, row_as_dict: Dict, upsert_based_on: List[str]):
    table_to_upset: Table = my_db_meta.tables[table_name]
    col_names: List[str] = table_to_upset.columns.keys()
    columns: str = f"{','.join(col_names)}"
    row_values: str = ','.join([f"'{row_as_dict[col_name]}'" for col_name in col_names])
    based_on_columns: str = ','.join(upsert_based_on)
    update_values: str = ','.join([f"{k} = '{v}'" for k, v in list(row_as_dict.items())])
    upsert_statement: str = f"""INSERT INTO {table_name} ({columns})
                                VALUES({row_values}) 
                                ON CONFLICT ({based_on_columns}) 
                                DO 
                                UPDATE SET {update_values};"""
    with engine.connect() as connection:
        connection.execute(upsert_statement)
