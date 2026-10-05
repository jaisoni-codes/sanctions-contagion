import json
import random
import os

SEED = 42
CUSTOMERS = 10000
COMPANIES = 3000

def generate_data():
    random.seed(SEED)
    os.makedirs("data/seed", exist_ok=True)
    
    # Generate basic parties
    parties = []
    for i in range(CUSTOMERS):
        parties.append({
            "party_id": f"CUST_{i}",
            "kind": "INDIVIDUAL",
            "name": f"Customer {i}",
            "country": "India",
            "country_of_residence": random.choice(["India", "UAE", "UK", "US", None]),
            "id_numbers": [f"ID_{i}"]
        })
        
    for i in range(COMPANIES):
        parties.append({
            "party_id": f"COMP_{i}",
            "kind": "COMPANY",
            "name": f"Company {i}",
            "country": "US",
            "country_of_residence": random.choice(["US", "Ireland", "Cayman", None]),
            "id_numbers": [f"CRN_{i}"]
        })
        
    edges = []
    # Generate some ownership edges
    doc_types = ["MoA", "AoA", "registry_filing", "stock_exchange_report", "declaration"]
    for i in range(100):
        edges.append({
            "edge_id": f"EDGE_{i}",
            "owner_id": f"CUST_{i}",
            "owned_id": f"COMP_{i}",
            "pct": 55.0,
            "source_doc": f"DOC_{i}.pdf",
            "doc_type": random.choice(doc_types)
        })

    with open("data/seed/parties.json", "w") as f:
        json.dump(parties, f, indent=2)
        
    with open("data/seed/edges.json", "w") as f:
        json.dump(edges, f, indent=2)
        
    print(f"Generated {len(parties)} parties.")

if __name__ == "__main__":
    generate_data()
