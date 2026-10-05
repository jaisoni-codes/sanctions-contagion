import json
import random
import os
import string

SEED = 42
CUSTOMERS = 10000
COMPANIES = 3000

def generate_data():
    random.seed(SEED)
    os.makedirs("data/seed", exist_ok=True)
    
    parties = []
    
    # Zipf-like names
    common_names = ["Mohammed Khan", "Rahul Sharma", "Amit Patel", "John Smith", "David Lee", "Wei Chen"]
    rare_names = [f"RareName {i}" for i in range(1000)]
    
    names_pool = []
    # Skewed distribution
    for i, name in enumerate(common_names):
        names_pool.extend([name] * (500 // (i + 1)))
    for name in rare_names:
        names_pool.append(name)
        
    for i in range(CUSTOMERS):
        parties.append({
            "party_id": f"CUST_{i}",
            "kind": "INDIVIDUAL",
            "name": random.choice(names_pool) if random.random() < 0.6 else f"Customer {i}",
            "country": "India",
            "country_of_residence": random.choice(["India", "UAE", "UK", "US", None]),
            "dob": f"19{random.randint(50, 99)}-0{random.randint(1,9)}-1{random.randint(0,9)}",
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
        
    # Plant neighbors for specific scenarios
    def plant_neighbor(pid, name, dob, ctry):
        parties.append({
            "party_id": pid, "kind": "INDIVIDUAL", "name": name, 
            "dob": dob, "country": ctry, "id_numbers": [pid]
        })

    # S01, S04, S05
    plant_neighbor("CUST_RAJEEV_1", "Rajeev Malhotra", "1980-01-01", "India") # Exact
    plant_neighbor("CUST_RAJEEV_2", "R. Malhotra", "1980-01-01", "India") # Initial
    plant_neighbor("CUST_RAJEEV_3", "Rajiv Malhotara", None, "India") # Missing DOB, spelling variant
    plant_neighbor("CUST_RAJEEV_4", "Rajeev Malhotra", "1990-12-12", "UK") # Homonym
    
    plant_neighbor("CUST_SUNITA_1", "Sunita", "1975-05-05", "India")
    
    # 500 Rahul Sharma
    for i in range(500):
        plant_neighbor(f"CUST_RAHUL_{i}", "Rahul Sharma", None if i > 10 else f"1980-01-{i%28+1}", "India")
        
    # 300 Mohammed Khan
    for i in range(300):
        plant_neighbor(f"CUST_MOHAMMED_{i}", "Mohammed Khan", f"1990-01-{i%28+1}", "UAE")

    # Edges
    edges = []
    # S04: Rajeev 30%, Sunita 25% of Delta Ltd
    parties.append({"party_id": "COMP_DELTA", "kind": "COMPANY", "name": "Delta Ltd", "country": "India"})
    edges.append({"edge_id": "E_S04_1", "owner_id": "CUST_RAJEEV_1", "owned_id": "COMP_DELTA", "pct": 30.0})
    edges.append({"edge_id": "E_S04_2", "owner_id": "CUST_SUNITA_1", "owned_id": "COMP_DELTA", "pct": 25.0})
    
    # S05: Rajeev 50% of Exact 50 Ltd
    parties.append({"party_id": "COMP_EXACT50", "kind": "COMPANY", "name": "Exact 50 Ltd", "country": "India"})
    edges.append({"edge_id": "E_S05_1", "owner_id": "CUST_RAJEEV_1", "owned_id": "COMP_EXACT50", "pct": 50.0})
    
    with open("data/seed/parties.json", "w") as f:
        json.dump(parties, f, indent=2)
        
    with open("data/seed/edges.json", "w") as f:
        json.dump(edges, f, indent=2)
        
    print(f"Generated {len(parties)} parties.")

if __name__ == "__main__":
    generate_data()
