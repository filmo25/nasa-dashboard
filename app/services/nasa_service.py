import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


TECHPORT_BASE_URL = "https://techport.nasa.gov/api"

NASA_API_KEY = os.getenv("NASA_API_KEY")

#TECHPORT_TOKEN = os.getenv("TECHPORT_TOKEN")


session = requests.Session()
session.headers.update({
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/152.0.0.0 Safari/537.36",
})


def refresh_api_token():
    print(">>> refresh_api_token() CALLED")
    response = session.get(
        f"{TECHPORT_BASE_URL}/nonce",
        params={"api_key": NASA_API_KEY},
        timeout=10,
    )

    print("========== TECHPORT NONCE DEBUG ==========")
    print("STATUS:", response.status_code)
    print("HEADERS:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    print("COOKIES:", session.cookies.get_dict())
    print("BODY:", response.text)
    print("==========================================")

    response.raise_for_status()

    authorization = response.headers.get("Authorization")

    print("AUTHORIZATION FOUND:", authorization is not None)

    if not authorization:
        raise RuntimeError(
            "TechPort /api/nonce did not return an Authorization header."
        )

    session.headers["Authorization"] = authorization

    return authorization


def techport_get(path, params=None):
    """
    Perform a GET request to the TechPort API.
    """
    if "Authorization" not in session.headers:
        refresh_api_token()

    url = f"{TECHPORT_BASE_URL}{path}"

    response = session.get(
        url,
        params=params,
        timeout=30,
    )

    if response.status_code == 401:
        refresh_api_token()

        response = session.get(
            url,
            params=params,
            timeout=30,
        )

    response.raise_for_status()

    return response.json()


def techport_post(path, json_body):
    """
    Perform a POST request to the TechPort API.

    TechPort requires a fresh nonce obtained from GET /api/nonce
    for every POST request.
    """

    # Get a fresh nonce
    nonce_response = session.get(
        f"{TECHPORT_BASE_URL}/nonce",
        params={"api_key": NASA_API_KEY},
        timeout=10,
    )

    nonce_response.raise_for_status()

    nonce = nonce_response.json()["nonce"]

    # Build a new payload so we don't modify the caller's dictionary
    payload = {
        **json_body,
        "nonce": nonce,
    }

    # Perform POST
    response = session.post(
        f"{TECHPORT_BASE_URL}{path}",
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


def fetch_statuses():
    """
    Retrieve the status enumeration from TechPort.

    Returns:
        list[dict]:
            [
                {"id": optional integer, "name": "Active"},
                {"id": optional integer, "name": "Inactive"},
                ...
            ]
    """
    payload = techport_get("/enums")

    enums = payload.get("enums", payload)

    if not isinstance(enums, dict):
        raise RuntimeError(
            "Unexpected response format from /api/enums."
        )

    status_candidates = [
        value
        for key, value in enums.items()
        if "status" in key.lower()
    ]

    for candidate in status_candidates:
        parsed = _parse_enum_values(candidate)

        if parsed:
            return parsed

    raise RuntimeError(
        "Could not find a status enumeration in /api/enums."
    )


def _parse_enum_values(value):
    """
    Convert different possible enum representations into:

        [{"id": ..., "name": ...}, ...]
    """
    result = []

    if isinstance(value, list):

        for item in value:

            if isinstance(item, str):
                result.append({
                    "id": None,
                    "name": item,
                })

            elif isinstance(item, dict):

                name = (
                    item.get("name")
                    or item.get("label")
                    or item.get("value")
                )

                item_id = (
                    item.get("id")
                    or item.get("enumId")
                    or item.get("key")
                )

                if name is not None:
                    result.append({
                        "id": _to_int_or_none(item_id),
                        "name": str(name),
                    })

    elif isinstance(value, dict):

        for key, item in value.items():

            if isinstance(item, str):

                result.append({
                    "id": _to_int_or_none(key),
                    "name": item,
                })

            elif isinstance(item, dict):

                name = (
                    item.get("name")
                    or item.get("label")
                    or item.get("value")
                )

                item_id = (
                    item.get("id")
                    or item.get("enumId")
                    or key
                )

                if name is not None:
                    result.append({
                        "id": _to_int_or_none(item_id),
                        "name": str(name),
                    })

    return result


def _to_int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


PROJECT_FIELDS = [
    "projectId",
    "title",
    "description",
    "status",
    "startDate",
    "endDate",
    "viewCount",
    "lastUpdated",
    "primaryTx",
    "additionalTxs",
    "states",
    "destinationTypes",
]


def fetch_top_projects(max_projects=3000, page_size=500):
    """
    Retrieve the most viewed projects from TechPort.

    The API search is sorted by viewCount descending.
    Pagination is used until max_projects have been collected.
    """
    projects = []
    offset = 0

    while len(projects) < max_projects:

        current_limit = min(
            page_size,
            max_projects - len(projects),
        )

        criteria = {
            "sortString": "viewCount desc",
            "fetchForListView": False,
            "fields": PROJECT_FIELDS,
            "limit": current_limit,
            "offset": offset,
        }

        payload = techport_post(
            "/projects/search",
            criteria,
        )

        batch = payload.get("results", [])

        if not isinstance(batch, list):
            raise RuntimeError(
                "Unexpected response format from "
                "/api/projects/search."
            )

        if not batch:
            break

        normalized_batch = []

        for item in batch:

            if isinstance(item, dict):
                normalized_batch.append(item)
                continue

            # Some API responses may provide IDs rather than objects.
            project_id = _extract_project_id(item)

            if project_id is None:
                raise RuntimeError(
                    "Could not determine a project ID "
                    "from a search result."
                )

            normalized_batch.append(
                fetch_project(project_id)
            )

        projects.extend(normalized_batch)

        offset += len(batch)

        if len(batch) < current_limit:
            break

        total = payload.get("total")

        if total is not None and offset >= int(total):
            break

    return projects[:max_projects]


def _extract_project_id(value):
    if isinstance(value, int):
        return value

    if isinstance(value, str):

        # Sometimes a result can itself be a JSON object string.
        try:
            parsed = json.loads(value)

            if isinstance(parsed, dict):
                value = parsed.get("projectId")

                if value is not None:
                    return _to_int_or_none(value)

        except json.JSONDecodeError:
            pass

        return _to_int_or_none(value)

    return None


def fetch_project(project_id):
    """
    Retrieve one complete TechPort project.
    """
    return techport_get(
        f"/projects/{project_id}"
    )


def fetch_taxonomy_category_map(projects):
    """
    Build a mapping:

        taxonomy node ID -> top-level TX category

    Example:

        123456 -> {"code": "TX04", "name": "Robotic Systems"}
    """
    root_ids = set()

    for project in projects:

        nodes = []

        primary = project.get("primaryTx")

        if primary:
            nodes.append(primary)

        additional = project.get("additionalTxs") or []
        nodes.extend(additional)

        for item in nodes:

            taxonomy_node = item.get("taxonomyNode")

            if taxonomy_node:
                root_id = taxonomy_node.get("taxonomyRootId")

                if root_id is not None:
                    root_ids.add(int(root_id))

    category_map = {}

    for root_id in root_ids:

        payload = techport_get(
            f"/taxonomies/nodes/{root_id}/tree"
        )

        tree = payload.get("taxonomyTree", [])

        _walk_taxonomy_tree(
            tree,
            None,
            category_map,
        )

    return category_map


def _walk_taxonomy_tree(nodes, current_category, category_map):

    for node in nodes:

        code = node.get("code")
        title = node.get("title")
        node_id = node.get("taxonomyNodeId")

        new_category = current_category

        if (
            isinstance(code, str)
            and re.fullmatch(r"TX\d{2}", code)
        ):
            new_category = {
                "code": code,
                "name": title,
            }

        if node_id is not None and new_category is not None:
            category_map[int(node_id)] = new_category

        children = node.get("children") or []

        _walk_taxonomy_tree(
            children,
            new_category,
            category_map,
        )

if __name__ == "__main__":
    token = refresh_api_token()
    print("Token received:", bool(token))