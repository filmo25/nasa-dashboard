from flask import Flask, jsonify, render_template

from app.db.connection import (
    get_connection,
    initialize_database,
)

from app.services.import_service import (
    import_projects as import_projects_service,
)

from app.services.project_service import (
    delete_projects as delete_projects_service,
)


app = Flask(__name__)


@app.route("/", methods=["GET"])
def get_index_page():
    """
    Render import.html.
    """
    initialize_database()

    connection = get_connection()

    try:

        database = connection.execute(
            """
            SELECT
                creation_date,
                last_update_date
            FROM database_info
            WHERE id = 1
            """
        ).fetchone()

        latest_update = connection.execute(
            """
            SELECT
                projects_added,
                projects_updated,
                projects_deleted
            FROM updates
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

        project_count = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM projects
            """
        ).fetchone()["count"]

    finally:
        connection.close()

    return render_template(
        "import.html",
        database_creation_date=(
            database["creation_date"]
            if database
            else None
        ),
        projects_added=(
            latest_update["projects_added"]
            if latest_update
            else 0
        ),
        projects_updated=(
            latest_update["projects_updated"]
            if latest_update
            else 0
        ),
        projects_deleted=(
            latest_update["projects_deleted"]
            if latest_update
            else 0
        ),
        has_projects=(project_count > 0),
    )


@app.route("/api/projects", methods=["POST"])
def import_projects():
    """
    Import the initial set of NASA projects.
    """
    try:

        db_update = import_projects_service()

        return jsonify({
            "status": "success",
            "db_update": db_update,
        }), 200

    except Exception as error:

        app.logger.exception(
            "NASA project import failed"
        )

        return jsonify({
            "status": "error",
            "message": str(error),
        }), 500


@app.route("/api/projects", methods=["DELETE"])
def delete_projects():
    """
    Delete all NASA projects.
    """
    try:

        result = delete_projects_service()

        return jsonify({
            "status": "success",
            **result,
        }), 200

    except Exception as error:

        app.logger.exception(
            "NASA project deletion failed"
        )

        return jsonify({
            "status": "error",
            "message": str(error),
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )