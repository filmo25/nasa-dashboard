import sqlite3
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "data" / "nasa.db"
SCHEMA_PATH = Path(__file__).resolve().with_name("schema.sql")


def get_connection():
    """
    Open a connection to the SQLite database.

    The database file is created automatically by SQLite
    if it does not already exist.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    # Foreign keys must be enabled for every SQLite connection.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """
    Create the database tables using schema.sql.

    Also create the single database_info row if necessary.
    """
    connection = get_connection()

    try:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(schema)

        row = connection.execute(
            """
            SELECT creation_date
            FROM database_info
            WHERE id = 1
            """
        ).fetchone()

        if row is None or row["creation_date"] is None:
            now = datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            )

            connection.execute(
                """
                INSERT OR REPLACE INTO database_info
                    (id, creation_date, last_update_date)
                VALUES
                    (1, ?, ?)
                """,
                (now, now),
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()