import pytest
import database
from app import app as flask_app

@pytest.fixture
def client(tmp_path):
    test_db = str(tmp_path / "test_ui.db")
    database.init_db(db_path=test_db, seed_sample_data=True)
    flask_app.config["TESTING"] = True
    database.DATABASE_NAME = test_db
    with flask_app.test_client() as client:
        yield client

def test_homepage_renders(client):
    res = client.get("/")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "Smart Campus Lost & Found Matcher" in html
    assert "Total Reports" in html
    assert "Active Cases" in html

def test_report_form_lost(client):
    res = client.get("/report/lost")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "Report a Lost Item" in html
    assert "Item Name *" in html

def test_report_form_found(client):
    res = client.get("/report/found")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "Report a Found Item" in html

def test_item_detail_and_matches(client):
    res = client.get("/item/1")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "Smart Similarity Matches" in html
    assert "Match Confidence" in html

def test_matches_matrix_page(client):
    res = client.get("/matches")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "Campus Smart Matching Matrix" in html
    assert "Vectorization" in html

def test_post_lost_item(client):
    post_data = {
        "name": "Sony Noise Canceling WH-1000XM5",
        "category": "Electronics",
        "colour": "Silver White",
        "location": "Student Union 3rd floor lounge",
        "description": "Premium silver wireless headphones in zip case with USB-C cable.",
        "contact_info": "tester@campus.edu"
    }
    res = client.post("/report/lost", data=post_data, follow_redirects=True)
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "Sony Noise Canceling WH-1000XM5" in html
    assert "Successfully recorded" in html
