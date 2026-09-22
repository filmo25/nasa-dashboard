# import needed python modules
from flask import Flask, render_template, jsonify
# the entry point uses backend services
import services

# define "main" as the web app entry point
main = Flask(__name__)

# http://localhost:5000/
# render import.html
@main.route('/', methods=['GET'])
def index():
    return render_template('import.html')

# http://localhost:5000/api/projects
# return json
@main.route('/api/projects', methods=['POST'])
def api_import_projects():
    # call the import projects service
    result = services.import_projects()
    
    # return database creation log as json
    return jsonify(result)

# run main
if __name__ == '__main__':
    main.run(debug=True)