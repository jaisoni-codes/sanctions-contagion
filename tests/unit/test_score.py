from engine.matching.normalize import normalize_party
from engine.matching.blocking import generate_blocking_keys
from engine.matching.score import score_pair

def test_exact_match():
    party = {
        "party_id": "P1",
        "kind": "INDIVIDUAL",
        "name": "Raju Mehra",
        "dob": "1980-01-01",
        "country": "India"
    }
    party["norm"] = normalize_party(party["name"], party["kind"])
    
    entry = {
        "entry_id": "E1",
        "entity_type": "INDIVIDUAL",
        "primary_name": "Raju Mehra",
        "dob": "1980-01-01",
        "countries": ["India"],
        "aliases_norm": []
    }
    entry["norm"] = normalize_party(entry["primary_name"], entry["entity_type"])
    
    res = score_pair(party, entry)
    assert res["tier"] == "STRONG"
    assert "DOB_EXACT" in res["reasons"]

def test_homonym_discounted():
    party = {
        "party_id": "P2",
        "kind": "INDIVIDUAL",
        "name": "Rahul Sharma",
        "dob": "1990-05-05",
        "country": "UK"
    }
    party["norm"] = normalize_party(party["name"], party["kind"])
    
    entry = {
        "entry_id": "E2",
        "entity_type": "INDIVIDUAL",
        "primary_name": "Rahul Sharma",
        "dob": "1985-02-02",
        "countries": ["India"],
        "aliases_norm": []
    }
    entry["norm"] = normalize_party(entry["primary_name"], entry["entity_type"])
    
    res = score_pair(party, entry)
    assert res["tier"] == "DISCOUNTED"
    assert "DOB_CONFLICT" in res["reasons"]
    assert "COUNTRY_CONFLICT" in res["reasons"]
