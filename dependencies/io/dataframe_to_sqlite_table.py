import logging
import sqlite3

import pandas as pd

logger = logging.getLogger(__name__)


def dataframe_to_sqlite_table(df: pd.DataFrame, db_path: str, table_name: str) -> str:
    try:
        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, if_exists="fail", index=False)
        conn.close()
        logger.info(
            "Sucessfully wrote DataFrame to database: %s, using table: %s.",
            db_path,
            table_name,
        )
    except Exception as e:
        logger.error(
            "Failed to write DataFrame to %s, using table %s.\nReason: %s",
            db_path,
            table_name,
            e,
        )
