import pytest
import matcher

def test_clean_text():
    raw = "  Hello, World! 123 -- Test..  "
    cleaned = matcher.clean_text(raw)
    assert cleaned == "hello world 123 test"

def test_build_item_text():
    item = {
        "name": "Hydro Flask",
        "category": "Bottles",
        "colour": "Blue",
        "location": "Library",
        "description": "Stainless steel flask with sticker"
    }
    text = matcher.build_item_text(item)
    assert "hydro flask" in text
    assert "blue" in text
    assert "library" in text

def test_matching_high_similarity():
    lost_item = {
        "id": 1,
        "name": "Silver MacBook Air 13 inch",
        "category": "Electronics",
        "colour": "Silver",
        "location": "Science Library",
        "description": "Left on 3rd floor desk near window. Has an Apple sticker."
    }
    found_item = {
        "id": 2,
        "name": "Apple MacBook laptop",
        "category": "Electronics",
        "colour": "Silver",
        "location": "Science Library 3rd floor",
        "description": "Found a silver Apple laptop on desk near the window."
    }
    irrelevant_item = {
        "id": 3,
        "name": "Red wool scarf",
        "category": "Clothing",
        "colour": "Red",
        "location": "Gymnasium",
        "description": "Knitted red scarf found on bleachers."
    }

    matches = matcher.find_matches_for_item(lost_item, [found_item, irrelevant_item])
    assert len(matches) > 0
    top_match = matches[0]
    assert top_match["id"] == 2
    assert top_match["match_percentage"] > 40.0

def test_find_all_campus_matches():
    lost_list = [
        {"id": 1, "name": "Keys", "category": "Keys", "colour": "Silver", "location": "Hall A", "description": "Set of 3 dorm keys"}
    ]
    found_list = [
        {"id": 2, "name": "Set of keys", "category": "Keys", "colour": "Silver", "location": "Hall A corridor", "description": "Keys found on floor"}
    ]
    pairings = matcher.find_all_campus_matches(lost_list, found_list)
    assert len(pairings) == 1
    assert pairings[0]["similarity_score"] > 0
