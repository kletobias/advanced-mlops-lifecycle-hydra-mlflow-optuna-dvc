import logging
import sqlite3

logger = logging.getLogger(__name__)


def get_column_info(db_path: str, table_name: str):
    column_info = {}
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
                column_type = column[2]
                column_info[column_name] = column_type
            conn.close()
            logger.info(
                "Got column column names and their dtypes for table %s",
                table_name,
            )
            return column_info
    except Exception as e:
        logger.error(
            "Failed to get column names and their dtypes for table %s\n%s",
            table_name,
            e,
        )
