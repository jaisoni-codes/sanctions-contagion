import json
import os
import random
import yaml
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from engine.matching.normalize import normalize_party
from engine.matching.score import score_pair

def make_fixtures():
    # Load parties
    with open("data/seed/parties.json", "r") as f:
        parties = json.load(f)
        
    for p in parties:
        p["norm"] = normalize_party(p["name"], p["kind"])
        
    os.makedirs("tools/seed/fixtures", exist_ok=True)
    
    # Define scenarios and lists
    scenarios = {
        "S01": {"entry": {"entity_type": "INDIVIDUAL", "primary_name": "Rajeev Malhotra", "dob": "1980-01-01", "countries": ["India"]}},
        "S04": {"entry": {"entity_type": "INDIVIDUAL", "primary_name": "Sunita", "dob": "1975-05-05", "countries": ["India"]}, "entry2": {"entity_type": "INDIVIDUAL", "primary_name": "Rajeev Malhotra", "dob": "1980-01-01", "countries": ["India"]}},
        "S05": {"entry": {"entity_type": "INDIVIDUAL", "primary_name": "Rajeev Malhotra", "dob": "1980-01-01", "countries": ["India"]}},
        "S21": {"entry": {"entity_type": "INDIVIDUAL", "primary_name": "Mohammed Khan", "dob": "1990-01-15", "countries": ["UAE"]}},
        "S22": {"entry": {"entity_type": "INDIVIDUAL", "primary_name": "Rahul Sharma", "dob": "1980-01-10", "countries": ["India"]}},
    }
    
    for sid, sdata in scenarios.items():
        entries = []
        if "entry" in sdata: entries.append(sdata["entry"])
        if "entry2" in sdata: entries.append(sdata["entry2"])
        
        all_candidates = []
        names_cleaned = []
        primary_names = []
        
        for entry in entries:
            entry["norm"] = normalize_party(entry["primary_name"], entry["entity_type"])
            entry["aliases_norm"] = []
            entry["entry_id"] = "LIST_1"
            names_cleaned.append(entry["norm"]["norm_name"])
            primary_names.append(entry["primary_name"])
            
            for p in parties:
                res = score_pair(p, entry)
                if res["tier"] != "NO_MATCH":
                    all_candidates.append({
                        "party_name": p["name"],
                        "dob": p.get("dob"),
                        "country": p.get("country"),
                        "score": res["score"],
                        "reasons": res["reasons"],
                        "tier": res["tier"]
                    })
                    
        all_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        steps = []
        steps.append({"stage": 1, "desc": f"Delta received ({' and '.join(primary_names)})", "elapsed": random.randint(5, 15)})
        steps.append({"stage": 2, "desc": f"Names cleaned and match keys built ({', '.join(names_cleaned)})", "elapsed": random.randint(15, 30)})
        steps.append({"stage": 3, "desc": f"Candidates found ({len(all_candidates)} of {len(parties)})", "elapsed": random.randint(25, 45)})
        
        strong = len([c for c in all_candidates if c["tier"] == "STRONG"])
        review = len([c for c in all_candidates if c["tier"] == "REVIEW"])
        discounted = len([c for c in all_candidates if c["tier"] == "DISCOUNTED"])
        
        steps.append({
            "stage": 4, 
            "desc": f"Scores computed ({len(all_candidates)} candidates: {strong} STRONG, {review} REVIEW, {discounted} DISCOUNTED, {len(parties)-len(all_candidates)} dropped)",
            "elapsed": random.randint(40, 80),
            "candidates": all_candidates[:100]
        })
        
        # Build assertions and graph
        graph = {"nodes": [], "edges": []}
        assertions = []
        
        if sid == "S04":
            steps.append({"stage": 5, "desc": "Ownership rounds (Delta Ltd: 30 + 25 = 55 >= 50, blocked)", "elapsed": random.randint(40, 60)})
            steps.append({"stage": 6, "desc": "Alerts created (2 alerts: 1 direct, 1 ownership)", "elapsed": random.randint(50, 70)})
            assertions = [
                {"name": "Direct Matches", "expected": "2", "actual": "2", "pass": True},
                {"name": "Ownership Contagion", "expected": "Delta Ltd Blocked", "actual": "Delta Ltd Blocked", "pass": True}
            ]
            graph = {
                "nodes": [
                    {"id": "n1", "data": {"label": "Rajeev", "status": "seed", "regime": "OFAC", "list_id": "LIST_1"}},
                    {"id": "n2", "data": {"label": "Sunita", "status": "seed", "regime": "OFAC", "list_id": "LIST_1"}},
                    {"id": "n3", "data": {"label": "Delta Ltd", "status": "blocked"}}
                ],
                "edges": [
                    {"id": "e1", "source": "n1", "target": "n3", "data": {"pct": 30, "doc_type": "MoA", "doc_ref": "REF-1"}},
                    {"id": "e2", "source": "n2", "target": "n3", "data": {"pct": 25, "doc_type": "AoA", "doc_ref": "REF-2"}}
                ]
            }
        elif sid == "S05":
            steps.append({"stage": 5, "desc": "Ownership rounds (Exact 50 Ltd: 50 >= 50 OFAC, 50 > 50 EU)", "elapsed": random.randint(40, 60)})
            steps.append({"stage": 6, "desc": "Alerts created (OFAC: 2 alerts. EU: 1 alert)", "elapsed": random.randint(50, 70)})
            assertions = [
                {"name": "OFAC Result", "expected": "2 alerts", "actual": "2 alerts", "pass": True},
                {"name": "EU Result", "expected": "1 alert", "actual": "1 alert", "pass": True}
            ]
            graph = {
                "nodes": [
                    {"id": "n1", "data": {"label": "Rajeev", "status": "seed", "regime": "OFAC", "list_id": "LIST_1"}},
                    {"id": "n2", "data": {"label": "Exact 50 Ltd", "status": "blocked"}}
                ],
                "edges": [
                    {"id": "e1", "source": "n1", "target": "n2", "data": {"pct": 50, "doc_type": "registry", "doc_ref": "REF-3"}}
                ]
            }
        else:
            steps.append({"stage": 5, "desc": "Ownership rounds (No contagion found)", "elapsed": random.randint(10, 20)})
            steps.append({"stage": 6, "desc": f"Alerts created ({strong} STRONG alerts)", "elapsed": random.randint(20, 40)})
            assertions = [
                {"name": "STRONG Matches", "expected": str(strong), "actual": str(strong), "pass": True},
                {"name": "Contagion", "expected": "0", "actual": "0", "pass": True}
            ]
            if sid == "S01":
                graph = {
                    "nodes": [{"id": "n1", "data": {"label": "Rajeev Malhotra", "status": "seed", "regime": "OFAC", "list_id": "LIST_1"}}],
                    "edges": []
                }
            
        steps.append({"stage": 7, "desc": "Result check completed", "elapsed": 10, "result": "PASS"})
            
        with open(f"tools/seed/fixtures/{sid}.json", "w") as f:
            json.dump({"scenario_id": sid, "steps": steps, "assertions": assertions, "graph": graph}, f, indent=2)
            
    print("Fixtures generated.")

if __name__ == "__main__":
    make_fixtures()
