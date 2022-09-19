from fastapi.testclient import TestClient
import json
import os

from API.main import app as fastapi_app

def test_countries():
    client = TestClient(fastapi_app)
    response = client.get("/latest/countries")
    assert response.status_code == 200
    res = response.json()
    assert res["type"] == "FeatureCollection"
    assert len(res["features"]) > 0
    for feature in res["features"]:
        assert feature["type"] == "Feature"
        assert type(feature["properties"]["name"]) == str
        print(feature["properties"]["name"])
        assert feature["geometry"]["type"] == "MultiPolygon"
        coordinates = feature["geometry"]["coordinates"]
        assert len(coordinates) == 1
        assert len(coordinates[0]) > 0
        for i in range(len(coordinates[0])):
            assert len(coordinates[0][i]) > 0
            for point in coordinates[0][i]:
                assert len(point) == 2
                assert type(point[0]) == float
                assert type(point[1]) == float
