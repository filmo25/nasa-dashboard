# the backend services uses db and cliet functions
from db import db
import client

# impot_projecst() orchestrates the fetching of data from the NASA API
# and the insertion of that data into the local sqlite database
def import_projects():

    # 1. create db
    db.create_db()
    

    # 2. fetch data (attributes and projects)
    
    # fetch and store all the nasa projects attributes
    # - statues
    # - technologies 
    # - destinations
    attributes = client.fetch_nasa_pjs_attributes()

    # fetch and store max 3k nasa mediatic relevant projects
    # * not yet implemented procedure *
    # projects = client.fetch_nasa_relevant_projects()
    

    # 3. populate attributes tables
    db.populate_attributes_tables(attributes)
    

    # 4. populate projects table
    # * not yet implemented function *
    # db.populate_projects_tables(projects)


    # 5. populate junction tables
    # * not yet implemented procedure *
    # db.populate_junctions_tables()


    # * not yet implemented procedure *
    # rows_added = count_projects_rows() 
    

    # return db update log in json
    return {
        "status": "success", 
        "added": "counting feature not yet implemented"
    }