import logging

from dependencies.io.dataframe_to_sqlite_table import dataframe_to_sqlite_table
from dependencies.io.sqlite_table_to_dataframe import sqlite_table_to_dataframe

logger = logging.getLogger(__name__)


def sqlite_table_to_new_db(current_db_path, table_name, new_output_path):
    try:
        df = sqlite_table_to_dataframe(current_db_path, table_name)
        logger.info("Created DataFrame from sqlite table: %s", table_name)
        dataframe_to_sqlite_table(df=df, db_path=new_output_path, table_name=table_name)
        logger.info("new_output_path: %s", new_output_path)
        logger.info("table_name: %s", table_name)
        logger.info(
            "Created new db at %s, with a single table %s",
            new_output_path,
            table_name,
        )
    except Exception as e:
        logger.error("Failed to create DataFrame from sqlite table to new db: %s", e)
