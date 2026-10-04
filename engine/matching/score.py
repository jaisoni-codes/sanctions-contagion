from rapidfuzz import fuzz
import jellyfish

T_STRONG = 0.90
T_REVIEW = 0.75

def compute_name_score(norm1, norm2):
    n1 = norm1.get("norm_name", "")
    n2 = norm2.get("norm_name", "")
    if not n1 or not n2:
        return 0.0
    
    # Token set similarity
    ts_sim = fuzz.token_set_ratio(n1, n2) / 100.0
    
    # Jaro-Winkler on sorted tokens
    st1 = " ".join(norm1.get("sorted_tokens", []))
    st2 = " ".join(norm2.get("sorted_tokens", []))
    jw_sim = jellyfish.jaro_winkler_similarity(st1, st2)
    
    # Phonetic overlap
    p1 = set(norm1.get("phonetics", []))
    p2 = set(norm2.get("phonetics", []))
    if p1 and p2:
        ph_overlap = len(p1.intersection(p2)) / max(len(p1), len(p2))
    else:
        ph_overlap = 0.0
        
    return 0.5 * ts_sim + 0.3 * jw_sim + 0.2 * ph_overlap

def score_pair(party, entry):
    reasons = []
    
    # Entity type mismatch
    if party.get("kind") != entry.get("entity_type"):
        return {"score": 0.0, "tier": "REJECT", "reasons": ["ENTITY_TYPE_MISMATCH"]}
        
    # Name scoring against all aliases (we assume entry["aliases"] contains dicts with norm_name etc)
    # For simplicity, if entry has no aliases, we score against its primary name
    best_name_score = compute_name_score(party.get("norm"), entry.get("norm"))
    matched_alias = entry.get("primary_name")
    
    for alias_norm in entry.get("aliases_norm", []):
        sc = compute_name_score(party.get("norm"), alias_norm)
        if sc > best_name_score:
            best_name_score = sc
            matched_alias = alias_norm.get("norm_name")
            
    score = best_name_score
    
    corroborators = 0
    
    # ID match
    party_ids = [id_val.get("value") if isinstance(id_val, dict) else str(id_val) for id_val in party.get("id_numbers", [])]
    entry_ids = [id_val.get("value") if isinstance(id_val, dict) else str(id_val) for id_val in entry.get("id_numbers", [])]
    
    id_match = False
    for pid in party_ids:
        if pid and pid in entry_ids:
            id_match = True
            break
            
    if id_match:
        score = max(score, 0.99)
        reasons.append("ID_EXACT")
        corroborators += 1
        
    # DOB
    party_dob = party.get("dob")
    entry_dob = entry.get("dob")
    dob_conflict = False
    if party_dob and entry_dob:
        if isinstance(entry_dob, list):
            # entry_dob might be list of dates
            e_dob = entry_dob[0]
        else:
            e_dob = entry_dob
            
        if party_dob == e_dob:
            score += 0.1
            reasons.append("DOB_EXACT")
            corroborators += 1
        elif party_dob[:4] == e_dob[:4]: # year match
            score += 0.05
            reasons.append("DOB_YEAR_ONLY")
        else:
            score -= 0.3
            reasons.append("DOB_CONFLICT")
            dob_conflict = True
    elif not party_dob or not entry_dob:
        reasons.append("MISSING_DOB")
        
    # Country
    party_country = party.get("country")
    entry_countries = entry.get("countries", [])
    country_conflict = False
    if party_country and entry_countries:
        if party_country in entry_countries:
            score += 0.05
            reasons.append("COUNTRY_MATCH")
            corroborators += 1
        else:
            score -= 0.05
            reasons.append("COUNTRY_CONFLICT")
            country_conflict = True
            
    score = min(max(score, 0.0), 1.0)
    
    tier = "NO_MATCH"
    if score >= T_STRONG and corroborators > 0:
        tier = "STRONG"
    elif score >= T_REVIEW:
        tier = "REVIEW"
        
    if dob_conflict and country_conflict:
        tier = "DISCOUNTED"
            
    if id_match:
        tier = "STRONG"
        
    return {
        "score": score,
        "tier": tier,
        "reasons": reasons,
        "matched_alias": matched_alias,
        "party_id": party.get("party_id"),
        "entry_id": entry.get("entry_id")
    }
