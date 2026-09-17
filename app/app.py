import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

NASA_API_KEY = os.getenv("NASA_API_KEY")
TECHPORT_BASE = "https://techport.nasa.gov/api"

session = requests.Session()
session.params = {
    "api_key": NASA_API_KEY,
}
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/152.0.0.0 Safari/537.36",
    "Accept": "application/json"
    })


def techport_get(path: str, params: dict | None = None):
    url = f"{TECHPORT_BASE}{path}"
    resp = session.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


@app.route("/test")
def test_techport():
    data = techport_get(
    "/projects",
    params={"updatedSince": "2026-01-01"}
    )
    return jsonify(data)



if __name__ == "__main__":
    app.run(debug=True, port=5000)