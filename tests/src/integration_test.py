from fastapi.testclient import TestClient
import json
import os

from API.main import app as fastapi_app

EXPECTED_OUT_DIR = os.path.join("tests", "expected")

def test_countries():
    client = TestClient(fastapi_app)
    response = client.get("/latest/countries")
    assert response.status_code == 200
    with open(os.path.join(EXPECTED_OUT_DIR, "countries.json"), "r") as json_file:
        assert response.json() == json.load(json_file)
