import pytest
import os
import database
from app import app as flask_app

@pytest.fixture
def client(tmp_path):
    test_db = str(tmp_path / "test.db")
    database.init_db(db_path=test_db, seed_sample_data=True)

    flask_app.config["TESTING"] = True
    database.DATABASE_NAME = test_db

    with flask_app.test_client() as client:
        yield client

def test_api_items(client):
    res = client.get("/api/items")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["items"]) > 0

def test_api_status_update(client):
    res = client.post("/api/item/1/status", json={"status": "Returned"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["new_status"] == "Returned"

    # Verify directly
    updated_item = database.get_item_by_id(1)
    assert updated_item["status"] == "Returned"

def test_api_item_matches(client):
    res = client.get("/api/item/1/matches")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "matches" in data
