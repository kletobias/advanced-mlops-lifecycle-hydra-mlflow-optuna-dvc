# dependencies/io/json_to_new_sqlite_db.py
# dependencies/io/json_to_sqlite.py
import logging

logger = logging.getLogger(__name__)
import decimal
import sqlite3

import ijson


def guess_sqlite_type(value: str) -> str:
    try:
        int(value)
        return "INTEGER"
    except (ValueError, TypeError):
        pass
    try:
        float(value)
        return "REAL"
    except (ValueError, TypeError):
        pass
    return "TEXT"


def json_to_new_sqlite_db(
    json_path: str,
    db_path: str,
    database_table_name: str,
    sample_size: int = 1000,
) -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    with open(json_path, "rb") as f:
        parser = ijson.items(f, "item")
        first_rows = []
        for i, row in enumerate(parser):
            if i < sample_size:
                first_rows.append(row)
            else:
                break
    if not first_rows:
        conn.close()
        return
    columns = {}
    for row in first_rows:
        for k, v in row.items():
            if k not in columns:
                columns[k] = guess_sqlite_type(v)
            else:
                if columns[k] == "TEXT":
                    continue
                new_type = guess_sqlite_type(v)
                if columns[k] == "REAL" and new_type == "INTEGER":
                    continue
                if columns[k] == "INTEGER" and new_type in ("REAL", "TEXT"):
                    columns[k] = "REAL" if new_type == "REAL" else "TEXT"
                if columns[k] == "REAL" and new_type == "TEXT":
                    columns[k] = "TEXT"
    table_cols = ", ".join(f'"{col}" {ctype}' for col, ctype in columns.items())
    create_stmt = f"CREATE TABLE IF NOT EXISTS {database_table_name} ({table_cols})"
    logger.info("Create statement:\n%s", create_stmt)
    c.execute(create_stmt)
    conn.commit()
    conn.close()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    placeholders = ", ".join(["?"] * len(columns))
    insert_stmt = f"INSERT INTO {database_table_name} VALUES ({placeholders})"
    logger.info("Insert statement:\n%s", insert_stmt)
    batch = []
    batch_size = 10000
    with open(json_path, "rb") as f:
        parser = ijson.items(f, "item")
        for row in parser:
            row_values = []
            for col in columns:
                value = row.get(col)
                if isinstance(value, decimal.Decimal):
                    value = float(value)
                row_values.append(value)
            batch.append(tuple(row_values))
            if len(batch) >= batch_size:
                c.executemany(insert_stmt, batch)
                conn.commit()
                batch.clear()
    if batch:
        c.executemany(insert_stmt, batch)
        conn.commit()
    conn.close()
    logger.info(
        "Done writing data to database: %s, table:%s",
        db_path,
        database_table_name,
    )
