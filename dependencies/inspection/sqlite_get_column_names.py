# dependencies/inspection/sqlite_get_column_names.py
# bin/data/sql/sqlite_get_column_names.py
import logging
import sqlite3

logger = logging.getLogger(__name__)


def sqlite_get_column_names(db_path: str, table_name: str):
    columns_list = []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if table_name in tables:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for column in columns:
                column_name = column[1]
                columns_list.append(column_name)

            conn.close()
            return columns_list
    except Exception as e:
        logger.error(
            "Failed to get column names from sqlite table %s\n:%s",
            table_name,
            e,
        )
