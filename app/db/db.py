import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "database.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

# List of US States for hardcoded loop
US_STATES = [
    ("AL", "Alabama"), ("AK", "Alaska"), ("AZ", "Arizona"), ("AR", "Arkansas"),
    ("CA", "California"), ("CO", "Colorado"), ("CT", "Connecticut"), ("DE", "Delaware"),
    ("FL", "Florida"), ("GA", "Georgia"), ("HI", "Hawaii"), ("ID", "Idaho"),
    ("IL", "Illinois"), ("IN", "Indiana"), ("IA", "Iowa"), ("KS", "Kansas"),
    ("KY", "Kentucky"), ("LA", "Louisiana"), ("ME", "Maine"), ("MD", "Maryland"),
    ("MA", "Massachusetts"), ("MI", "Michigan"), ("MN", "Minnesota"), ("MS", "Mississippi"),
    ("MO", "Missouri"), ("MT", "Montana"), ("NE", "Nebraska"), ("NV", "Nevada"),
    ("NH", "New Hampshire"), ("NJ", "New Jersey"), ("NM", "New Mexico"), ("NY", "New York"),
    ("NC", "North Carolina"), ("ND", "North Dakota"), ("OH", "Ohio"), ("OK", "Oklahoma"),
    ("OR", "Oregon"), ("PA", "Pennsylvania"), ("RI", "Rhode Island"), ("SC", "South Carolina"),
    ("SD", "South Dakota"), ("TN", "Tennessee"), ("TX", "Texas"), ("UT", "Utah"),
    ("VT", "Vermont"), ("VA", "Virginia"), ("WA", "Washington"), ("WV", "West Virginia"),
    ("WI", "Wisconsin"), ("WY", "Wyoming")
]

def create_db():
    """Creates directory and executes schema.sql."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()


def populate_statuses(statuses, cursor):
    """Inserts project status types into DB."""
    for status in statuses:
        cursor.execute(
            "INSERT OR IGNORE INTO statuses (name) VALUES (?)",
            (status.get("value"),)
        )


def populate_technologies(technologies, cursor):
    """Inserts taxonomy technology nodes into DB."""
    for tech in technologies:
        content = tech.get("content", {})
        cursor.execute(
            "INSERT OR IGNORE INTO technologies (id, code, name) VALUES (?, ?, ?)",
            (content.get("taxonomyNodeId"), content.get("code"), content.get("title"))
        )


def populate_states(cursor):
    """Populates US States into DB."""
    for code, name in US_STATES:
        cursor.execute(
            "INSERT OR IGNORE INTO states (name) VALUES (?)",
            (name,)
        )


def populate_destinations(destinations, cursor):
    """Inserts destination types into DB."""
    for dest in destinations:
        cursor.execute(
            "INSERT OR IGNORE INTO destinations (name) VALUES (?)",
            (dest.get("label"),)
        )


def populate_attributes_tables(attributes):
    """
    Subdivided orchestrator for attributes DB insertion.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    populate_statuses(attributes.get("statuses", []), cursor)
    populate_technologies(attributes.get("technologies", []), cursor)
    populate_states(cursor)
    populate_destinations(attributes.get("destinations", []), cursor)

    conn.commit()
    conn.close()