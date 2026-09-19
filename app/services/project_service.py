from datetime import datetime, timezone

from app.db.connection import (
    get_connection,
    initialize_database,
)


def delete_projects():
    """
    Delete all projects from the database.

    Related rows in pj_tech, pj_states and pj_dest are
    automatically deleted through ON DELETE CASCADE.
    """
    initialize_database()

    connection = get_connection()

    try:

        row = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM projects
            """
        ).fetchone()

        deleted_count = row["count"]

        connection.execute(
            "DELETE FROM projects"
        )

        now = datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        )

        connection.execute(
            """
            UPDATE database_info
            SET last_update_date = ?
            WHERE id = 1
            """,
            (now,),
        )

        connection.commit()

        return {
            "deleted": deleted_count
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()