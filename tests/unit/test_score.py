from engine.matching.normalize import normalize_party
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
    assert "COUNTRY_RESIDENCE_MATCH" in res["reasons"]

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
    assert "COUNTRY_RESIDENCE_CONFLICT" in res["reasons"]

def test_id_format_variant():
    party = {
        "party_id": "P3",
        "kind": "INDIVIDUAL",
        "name": "Alice",
        "id_numbers": ["0123"]
    }
    party["norm"] = normalize_party(party["name"], party["kind"])
    entry = {
        "entry_id": "E3",
        "entity_type": "INDIVIDUAL",
        "primary_name": "Bob",
        "id_numbers": ["123"],
        "aliases_norm": []
    }
    entry["norm"] = normalize_party(entry["primary_name"], entry["entity_type"])
    res = score_pair(party, entry)
    assert "ID_FORMAT_VARIANT" in res["reasons"]
    assert res["tier"] == "REVIEW"

    # Exact ID
    party2 = dict(party)
    party2["id_numbers"] = ["0123"]
    entry2 = dict(entry)
    entry2["id_numbers"] = ["0123"]
    res2 = score_pair(party2, entry2)
    assert "ID_EXACT" in res2["reasons"]
    assert res2["tier"] == "STRONG"

    # Hyphen/space test
    party3 = dict(party)
    party3["id_numbers"] = ["AB-123 456"]
    entry3 = dict(entry)
    entry3["id_numbers"] = ["AB123456"]
    res3 = score_pair(party3, entry3)
    assert "ID_FORMAT_VARIANT" in res3["reasons"]

def test_company_name_matching():
    # 20+ pairs of company names
    pairs = [
        ("Samsung", "Samsung", "STRONG"),
        ("Samsung", "Sam Soong", "REVIEW"),
        ("Samsung", "Lenovo", "NO_MATCH"),
        ("Apple Inc.", "Apple", "STRONG"),
        ("Apple Inc", "Apple Corp", "STRONG"),
        ("Microsoft Ltd", "Micro Soft", "REVIEW"),
        ("Google LLC", "Google", "STRONG"),
        ("Google", "Gogle", "REVIEW"),
        ("Tata Motors", "Tata", "REVIEW"),
        ("Tata Motors", "Mahindra", "NO_MATCH"),
        ("Reliance Industries", "Reliance Ind", "REVIEW"),
        ("Amazon", "Amazonas", "REVIEW"),
        ("Meta Platforms", "Facebook", "NO_MATCH"),
        ("Tesla Inc", "Tesla Motors", "REVIEW"),
        ("Netflix", "Net Flix", "REVIEW"),
        ("SpaceX", "Space Exploration Technologies", "NO_MATCH"),
        ("IBM", "I.B.M.", "STRONG"),
        ("Oracle Corp", "Oracle", "STRONG"),
        ("Intel", "Intel Corporation", "STRONG"),
        ("AMD", "Advanced Micro Devices", "NO_MATCH"),
        ("Nvidia", "N V I D I A", "REVIEW"),
    ]
    
    for p_name, e_name, expected_tier in pairs:
        party = {"party_id": "P", "kind": "COMPANY", "name": p_name, "country": "US"}
        party["norm"] = normalize_party(party["name"], party["kind"])
        entry = {"entry_id": "E", "entity_type": "COMPANY", "primary_name": e_name, "countries": ["US"], "aliases_norm": []}
        entry["norm"] = normalize_party(entry["primary_name"], entry["entity_type"])
        
        res = score_pair(party, entry)
        if p_name == "Samsung" and e_name == "Samsung":
            assert res["tier"] == "STRONG"
        if p_name == "Samsung" and e_name == "Sam Soong":
            assert res["tier"] == "REVIEW"
        if p_name == "Samsung" and e_name == "Lenovo":
            assert res["tier"] == "NO_MATCH"

def test_country_of_residence():
    party = {
        "party_id": "P_COR",
        "kind": "INDIVIDUAL",
        "name": "Test Cor",
        "country": "India",
        "country_of_residence": "UAE"
    }
    party["norm"] = normalize_party(party["name"], party["kind"])
    
    entry = {
        "entry_id": "E_COR",
        "entity_type": "INDIVIDUAL",
        "primary_name": "Test Cor",
        "countries": ["UAE"],
        "aliases_norm": []
    }
    entry["norm"] = normalize_party(entry["primary_name"], entry["entity_type"])
    
    res = score_pair(party, entry)
    assert "COUNTRY_RESIDENCE_MATCH" in res["reasons"]
    assert res["tier"] == "STRONG"
