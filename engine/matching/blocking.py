import itertools

def generate_blocking_keys(norm_data: dict, id_numbers: list = None, dob: str = None) -> list:
    keys = set()
    phonetics = norm_data.get("phonetics", [])
    
    # Pairs of phonetic tokens
    if len(phonetics) >= 2:
        for p1, p2 in itertools.combinations(phonetics, 2):
            keys.add(f"PHON_{p1}_{p2}")
            keys.add(f"PHON_{p2}_{p1}")
    elif len(phonetics) == 1:
        keys.add(f"PHON_{phonetics[0]}")
        
    # Exact ID numbers
    if id_numbers:
        for id_val in id_numbers:
            if isinstance(id_val, dict) and 'value' in id_val:
                keys.add(f"ID_{id_val['value']}")
            elif isinstance(id_val, str):
                keys.add(f"ID_{id_val}")
                
    # Name plus birth year
    if dob:
        year = dob[:4] # assuming YYYY...
        norm_name = norm_data.get("norm_name", "").replace(" ", "")
        if norm_name and year:
            keys.add(f"NAME_DOB_{norm_name}_{year}")
            
    return list(keys)
