from flask import Flask, render_template, jsonify
import services

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('import.html')

@app.route('/api/projects', methods=['POST'])
def api_import_projects():
    # Call the service orchestrator
    result = services.import_projects()
    
    # Return the dictionary as a JSON response
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)