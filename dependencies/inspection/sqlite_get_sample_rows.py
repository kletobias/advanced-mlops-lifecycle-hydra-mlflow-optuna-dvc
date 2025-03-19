# bin/data/sql/sqlite_get_sample_rows.py
import logging
import sqlite3
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def sqlite_get_sample_rows(
    db_path: str,
    table_name: str,
    random: bool = False,
    n: int = 10,
) -> pd.DataFrame | None:
    """Retrieves a sample of rows from a specified table in an SQLite database.

    Args:
    ----
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the table to query.
        random (bool, optional): If True, returns a random sample of rows. Defaults to False.
        n (int, optional): Number of rows to retrieve. Defaults to 10.

    Returns:
    -------
        Optional[pd.DataFrame]: DataFrame containing the sampled rows, or None if an error occurs.
    """
    # Validate inputs
    if not Path(db_path).is_file():
        logger.error("Database file does not exist: %s", db_path)
        return None

    if not isinstance(table_name, str) or not table_name.isidentifier():
        logger.error("Invalid table name: %s", table_name)
        return None

    query = f"SELECT * FROM {table_name} "
    if random:
        query += "ORDER BY RANDOM() LIMIT ?;"
    else:
        query += "LIMIT ?;"

    try:
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(query, conn, params=(n,))
        logger.info("Successfully retrieved %d rows from table '%s'.", n, table_name)
        return df
    except sqlite3.OperationalError as oe:
        logger.error(
            "SQLite operational error: %s. Database: %s, Table: %s",
            oe,
            db_path,
            table_name,
        )
    except pd.io.sql.DatabaseError as de:
        logger.error("Pandas DatabaseError: %s. Query: %s", de, query)
    except Exception as e:
        logger.error(
            "Unexpected error: %s. Database: %s, Table: %s",
            e,
            db_path,
            table_name,
        )

    return None  # Return None if any exception occurs
