from datetime import datetime, timezone


from app.db.connection import (
    get_connection,
    initialize_database,
)

from app.services.nasa_service import (
    fetch_statuses,
    fetch_taxonomy_category_map,
    fetch_top_projects,
)


MAX_PROJECTS = 3000


def import_projects():
    """
    Perform the initial NASA project import.

    The database must not already contain projects.
    """
    initialize_database()

    # Fetch data BEFORE opening the write transaction.
    statuses = fetch_statuses()
    projects = fetch_top_projects(
        max_projects=MAX_PROJECTS
    )

    if not projects:
        raise RuntimeError(
            "TechPort returned no projects."
        )

    taxonomy_map = fetch_taxonomy_category_map(
        projects
    )

    connection = get_connection()

    try:

        existing_count = connection.execute(
            "SELECT COUNT(*) AS count FROM projects"
        ).fetchone()["count"]

        if existing_count > 0:
            raise RuntimeError(
                "The database already contains projects. "
                "Delete the projects first or use the update "
                "function."
            )

        status_map = _sync_statuses(
            connection,
            statuses,
        )

        added_count = 0

        for project in projects:

            project_id = int(project["projectId"])

            status_id = _get_or_create_status_id(
                connection,
                status_map,
                project.get("status"),
            )

            connection.execute(
                """
                INSERT INTO projects (
                    id,
                    title,
                    description,
                    start_date,
                    end_date,
                    status_id,
                    view_count,
                    last_updated
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    project.get("title"),
                    project.get("description"),
                    project.get("startDate"),
                    project.get("endDate"),
                    status_id,
                    project.get("viewCount", 0),
                    project.get("lastUpdated"),
                ),
            )

            _insert_project_states(
                connection,
                project_id,
                project.get("states") or [],
            )

            _insert_project_destinations(
                connection,
                project_id,
                project.get("destinationTypes") or [],
            )

            _insert_project_technologies(
                connection,
                project_id,
                project,
                taxonomy_map,
            )

            added_count += 1

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

        connection.execute(
            """
            INSERT INTO updates (
                date,
                projects_added,
                projects_updated,
                projects_deleted
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                now,
                added_count,
                0,
                0,
            ),
        )

        connection.commit()

        creation_row = connection.execute(
            """
            SELECT creation_date
            FROM database_info
            WHERE id = 1
            """
        ).fetchone()

        return {
            "database_creation_date": (
                creation_row["creation_date"]
                if creation_row
                else None
            ),
            "projects_added": added_count,
            "projects_updated": 0,
            "projects_deleted": 0,
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def _sync_statuses(connection, statuses):
    """
    Insert status values into the local status table.

    Existing rows are reused so project status_id values
    remain stable.
    """
    status_map = {}

    for status in statuses:

        name = status["name"].strip()

        if not name:
            continue

        existing = connection.execute(
            """
            SELECT id
            FROM status
            WHERE name = ?
            """,
            (name,),
        ).fetchone()

        if existing:

            status_id = existing["id"]

        elif status["id"] is not None:

            status_id = status["id"]

            connection.execute(
                """
                INSERT OR IGNORE INTO status (id, name)
                VALUES (?, ?)
                """,
                (status_id, name),
            )

        else:

            row = connection.execute(
                """
                SELECT COALESCE(MAX(id), 0) + 1 AS next_id
                FROM status
                """
            ).fetchone()

            status_id = row["next_id"]

            connection.execute(
                """
                INSERT INTO status (id, name)
                VALUES (?, ?)
                """,
                (status_id, name),
            )

        status_map[name.lower()] = status_id

    return status_map


def _get_or_create_status_id(
    connection,
    status_map,
    status_name,
):
    if status_name is None:
        return None

    normalized = str(status_name).strip().lower()

    if normalized in status_map:
        return status_map[normalized]

    # Safety fallback if a project contains a status not
    # present in the enum response.
    existing = connection.execute(
        """
        SELECT id
        FROM status
        WHERE LOWER(name) = ?
        """,
        (normalized,),
    ).fetchone()

    if existing:
        status_map[normalized] = existing["id"]
        return existing["id"]

    next_id = connection.execute(
        """
        SELECT COALESCE(MAX(id), 0) + 1 AS next_id
        FROM status
        """
    ).fetchone()["next_id"]

    connection.execute(
        """
        INSERT INTO status (id, name)
        VALUES (?, ?)
        """,
        (next_id, status_name),
    )

    status_map[normalized] = next_id

    return next_id


def _insert_project_states(
    connection,
    project_id,
    states,
):
    for state in states:

        state_id = state.get("stateTerritoryId")
        name = state.get("name")

        if state_id is None or not name:
            continue

        connection.execute(
            """
            INSERT OR IGNORE INTO states (id, name)
            VALUES (?, ?)
            """,
            (
                int(state_id),
                name,
            ),
        )

        connection.execute(
            """
            INSERT OR IGNORE INTO pj_states (
                project_id,
                state_id
            )
            VALUES (?, ?)
            """,
            (
                project_id,
                int(state_id),
            ),
        )


def _insert_project_destinations(
    connection,
    project_id,
    destinations,
):
    for name in destinations:

        if not name:
            continue

        existing = connection.execute(
            """
            SELECT id
            FROM destinations
            WHERE name = ?
            """,
            (name,),
        ).fetchone()

        if existing:

            destination_id = existing["id"]

        else:

            destination_id = connection.execute(
                """
                SELECT COALESCE(MAX(id), 0) + 1 AS next_id
                FROM destinations
                """
            ).fetchone()["next_id"]

            connection.execute(
                """
                INSERT INTO destinations (id, name)
                VALUES (?, ?)
                """,
                (
                    destination_id,
                    name,
                ),
            )

        connection.execute(
            """
            INSERT OR IGNORE INTO pj_dest (
                project_id,
                destination_id
            )
            VALUES (?, ?)
            """,
            (
                project_id,
                destination_id,
            ),
        )


def _insert_project_technologies(
    connection,
    project_id,
    project,
    taxonomy_map,
):
    nodes = []

    primary = project.get("primaryTx")

    if primary:
        nodes.append(primary)

    nodes.extend(project.get("additionalTxs") or [])

    category_keys = set()

    for item in nodes:

        taxonomy_node = item.get("taxonomyNode")

        if not taxonomy_node:
            continue

        node_id = taxonomy_node.get("taxonomyNodeId")

        if node_id is None:
            continue

        category = taxonomy_map.get(
            int(node_id)
        )

        if category is None:
            continue

        category_keys.add(
            (
                category["code"],
                category["name"],
            )
        )

    for code, name in category_keys:

        existing = connection.execute(
            """
            SELECT id
            FROM technologies
            WHERE code = ?
            """,
            (code,),
        ).fetchone()

        if existing:

            technology_id = existing["id"]

        else:

            technology_id = connection.execute(
                """
                SELECT COALESCE(MAX(id), 0) + 1 AS next_id
                FROM technologies
                """
            ).fetchone()["next_id"]

            connection.execute(
                """
                INSERT INTO technologies (
                    id,
                    code,
                    name
                )
                VALUES (?, ?, ?)
                """,
                (
                    technology_id,
                    code,
                    name,
                ),
            )

        connection.execute(
            """
            INSERT OR IGNORE INTO pj_tech (
                project_id,
                technology_id
            )
            VALUES (?, ?)
            """,
            (
                project_id,
                technology_id,
            ),
        )