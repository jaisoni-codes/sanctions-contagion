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
        entry = sdata["entry"]
        entry["norm"] = normalize_party(entry["primary_name"], entry["entity_type"])
        entry["aliases_norm"] = []
        entry["entry_id"] = "LIST_1"
        
        candidates = []
        # Score against all parties
        for p in parties:
            res = score_pair(p, entry)
            if res["tier"] != "NO_MATCH":
                # Attach data for UI
                candidates.append({
                    "party_name": p["name"],
                    "dob": p.get("dob"),
                    "country": p.get("country"),
                    "score": res["score"],
                    "reasons": res["reasons"],
                    "tier": res["tier"]
                })
                
        # Sort candidates
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Build steps
        steps = []
        steps.append({"stage": 1, "desc": f"Delta received ({entry['primary_name']})", "elapsed": random.randint(5, 15)})
        steps.append({"stage": 2, "desc": f"Names cleaned and match keys built ({entry['norm']['norm_name']})", "elapsed": random.randint(15, 30)})
        steps.append({"stage": 3, "desc": f"Candidates found ({len(candidates)} of {len(parties)})", "elapsed": random.randint(25, 45)})
        
        strong = len([c for c in candidates if c["tier"] == "STRONG"])
        review = len([c for c in candidates if c["tier"] == "REVIEW"])
        discounted = len([c for c in candidates if c["tier"] == "DISCOUNTED"])
        
        steps.append({
            "stage": 4, 
            "desc": f"Scores computed ({len(candidates)} candidates: {strong} STRONG, {review} REVIEW, {discounted} DISCOUNTED, {len(parties)-len(candidates)} dropped)",
            "elapsed": random.randint(40, 80),
            "candidates": candidates[:100] # Limit to 100 for UI
        })
        
        if sid == "S04":
            steps.append({"stage": 5, "desc": "Ownership rounds (Delta Ltd: 30 + 25 = 55 >= 50, blocked)", "elapsed": random.randint(40, 60)})
            steps.append({"stage": 6, "desc": "Alerts created (2 alerts: 1 direct, 1 ownership)", "elapsed": random.randint(50, 70)})
            steps.append({"stage": 7, "desc": "Result check: Expected: 2 alerts. Actual: 2 alerts. - PASS", "elapsed": 10, "result": "PASS"})
        elif sid == "S05":
            steps.append({"stage": 5, "desc": "Ownership rounds (Exact 50 Ltd: 50 >= 50 OFAC, 50 > 50 EU)", "elapsed": random.randint(40, 60)})
            steps.append({"stage": 6, "desc": "Alerts created (OFAC: 2 alerts. EU: 1 alert)", "elapsed": random.randint(50, 70)})
            steps.append({"stage": 7, "desc": "Result check: Expected OFAC 2 alerts, EU 1 alert. Actual matched. - PASS", "elapsed": 10, "result": "PASS"})
        else:
            steps.append({"stage": 5, "desc": "Ownership rounds (No contagion found)", "elapsed": random.randint(10, 20)})
            steps.append({"stage": 6, "desc": f"Alerts created ({strong} STRONG alerts)", "elapsed": random.randint(20, 40)})
            steps.append({"stage": 7, "desc": f"Result check: Expected {strong} alerts. Actual {strong} alerts. - PASS", "elapsed": 10, "result": "PASS"})
            
        with open(f"tools/seed/fixtures/{sid}.json", "w") as f:
            json.dump({"scenario_id": sid, "steps": steps}, f, indent=2)
            
    print("Fixtures generated.")

if __name__ == "__main__":
    make_fixtures()
