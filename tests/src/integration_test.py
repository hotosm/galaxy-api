from fastapi.testclient import TestClient

from API.main import app as fastapi_app

client = TestClient(fastapi_app)
usernames = ["mspray6", "mspray7"]

def test_countries():
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

def test_osm_users_ids_OK():
    response = client.post("/latest/osm-users/ids/", json={"userNames":usernames,"fromTimestamp":"2018-07-11T00:00:00Z","toTimestamp":"2018-07-12T00:00:00Z"})
    assert response.status_code == 200
    res = response.json()
    assert len(res) == len(usernames)
    for i in range(len(res)):
        assert type(res[i]["userId"]) == int
        assert res[i]["userName"] == usernames[i]

def test_osm_users_ids_old_date():
    response = client.post("/latest/osm-users/ids/", json={"userNames":usernames,"fromTimestamp":"2000-07-11T00:00:00Z","toTimestamp":"2000-07-12T00:00:00Z"})
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_osm_users_ids_no_user():
    response = client.post("/latest/osm-users/ids/", json={"userNames":[],"fromTimestamp":"2018-07-11T00:00:00Z","toTimestamp":"2018-07-12T00:00:00Z"})
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_osm_users_ids_missing_param():
    response = client.post("/latest/osm-users/ids/", json={"fromTimestamp":"2018-07-11T00:00:00Z","toTimestamp":"2018-07-12T00:00:00Z"})
    assert response.status_code == 422
    response = client.post("/latest/osm-users/ids/", json={"userNames":usernames,"toTimestamp":"2018-07-12T00:00:00Z"})
    assert response.status_code == 422
    response = client.post("/latest/osm-users/ids/", json={"userNames":usernames,"fromTimestamp":"2018-07-11T00:00:00Z"})
    assert response.status_code == 422

def test_osm_users_ids_bad_timestamp_order():
    response = client.post("/latest/osm-users/ids/", json={"userNames":usernames,"fromTimestamp":"2018-07-11T00:00:00Z","toTimestamp":"2018-07-10T00:00:00Z"})
    assert response.status_code == 422
