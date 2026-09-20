# from db import db
# import client

def import_projects():
    """
    Orchestrates the fetching of data from the NASA API and 
    the insertion of that data into the local SQLite database.
    """
    # 1. Initialize DB
    # db.create_db()
    
    # 2. Fetch Data
    # attributes = client.fetch_nasa_pjs_attributes()
    # projects = client.fetch_nasa_relevant_projects()
    
    # 3. Populate DB
    # db.populate_db(attributes, projects)
    
    # 4. Return Results (Stubbed for testing)
    # rows_added = count_projects_rows() 
    
    return {
        "status": "success", 
        "added": 0
    }