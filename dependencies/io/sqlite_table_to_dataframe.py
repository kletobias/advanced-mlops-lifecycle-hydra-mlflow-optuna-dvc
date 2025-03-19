import logging

logger = logging.getLogger(__name__)
import sqlite3

import pandas as pd


def sqlite_table_to_dataframe(db_path: str, table_name: str) -> pd.DataFrame:
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)
        conn.close()
        logger.info("Sucessfully created DataFrame from %s", table_name)
        return df
    except Exception as e:
        logger.info(
            "Failed to create DataFrame from table %s, Reason: %s.",
            table_name,
            e,
        )
