from engine.ownership import compute_ownership_contagion_reference

def test_tp_chain():
    # A -> 60% -> B -> 55% -> C
    seeds = {"A"}
    edges = [
        {"owner_id": "A", "owned_id": "B", "pct": 60.0},
        {"owner_id": "B", "owned_id": "C", "pct": 55.0}
    ]
    derived = compute_ownership_contagion_reference(seeds, edges)
    assert "B" in derived
    assert "C" in derived

def test_tp_agg():
    # A(blocked) 30% -> C, B(blocked) 25% -> C
    seeds = {"A", "B"}
    edges = [
        {"owner_id": "A", "owned_id": "C", "pct": 30.0},
        {"owner_id": "B", "owned_id": "C", "pct": 25.0}
    ]
    derived = compute_ownership_contagion_reference(seeds, edges)
    assert "C" in derived
    assert derived["C"]["total_pct"] == 55.0

def test_tp_cycle():
    # A(blocked) -> 60% -> B -> 60% -> C -> 60% -> B (cycle)
    seeds = {"A"}
    edges = [
        {"owner_id": "A", "owned_id": "B", "pct": 60.0},
        {"owner_id": "B", "owned_id": "C", "pct": 60.0},
        {"owner_id": "C", "owned_id": "B", "pct": 60.0}
    ]
    derived = compute_ownership_contagion_reference(seeds, edges)
    assert "B" in derived
    assert "C" in derived

def test_tn_near():
    # A(blocked) -> 49.9% -> B
    seeds = {"A"}
    edges = [
        {"owner_id": "A", "owned_id": "B", "pct": 49.9}
    ]
    derived = compute_ownership_contagion_reference(seeds, edges)
    assert "B" not in derived
