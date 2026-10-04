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
        })
        
    for i in range(COMPANIES):
        parties.append({
            "party_id": f"COMP_{i}",
            "kind": "COMPANY",
            "name": f"Company {i}",
        })

    with open("data/seed/parties.json", "w") as f:
        json.dump(parties, f, indent=2)
        
    print(f"Generated {len(parties)} parties.")

if __name__ == "__main__":
    generate_data()
