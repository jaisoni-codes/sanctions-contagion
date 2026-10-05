import re
from rapidfuzz import fuzz
import jellyfish

T_STRONG = 0.90
T_REVIEW = 0.75

def compute_name_score(norm1, norm2, kind=None):
    n1 = norm1.get("norm_name", "")
    n2 = norm2.get("norm_name", "")
    if not n1 or not n2:
        return 0.0
        
    if kind == "COMPANY":
        # Check brand / joined name phonetics
        jn1 = norm1.get("joined_name", "")
        jn2 = norm2.get("joined_name", "")
        if jn1 and jn2 and jn1 == jn2:
            return 0.95
        pj1 = norm1.get("phonetic_joined", "")
        pj2 = norm2.get("phonetic_joined", "")
        if pj1 and pj2 and pj1 == pj2:
            return 0.84 # Partial match for sound-alike brands (e.g. Samsung vs Sam Soong)
            
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

def clean_id(val):
    if not isinstance(val, str):
        val = str(val)
    return val.strip()

def super_clean_id(val):
    val = clean_id(val)
    val = re.sub(r'[\s\-]', '', val)
    val = val.lstrip('0')
    return val

def score_pair(party, entry):
    reasons = []
    
    # Entity type mismatch
    if party.get("kind") != entry.get("entity_type"):
        return {"score": 0.0, "tier": "REJECT", "reasons": ["ENTITY_TYPE_MISMATCH"]}
        
    kind = party.get("kind")
        
    best_name_score = compute_name_score(party.get("norm"), entry.get("norm"), kind=kind)
    matched_alias = entry.get("primary_name")
    
    for alias_norm in entry.get("aliases_norm", []):
        sc = compute_name_score(party.get("norm"), alias_norm, kind=kind)
        if sc > best_name_score:
            best_name_score = sc
            matched_alias = alias_norm.get("norm_name")
            
    score = best_name_score
    
    corroborators = 0
    
    # Item 1: Identifiers
    party_ids = [clean_id(id_val.get("value") if isinstance(id_val, dict) else id_val) for id_val in party.get("id_numbers", []) if id_val]
    entry_ids = [clean_id(id_val.get("value") if isinstance(id_val, dict) else id_val) for id_val in entry.get("id_numbers", []) if id_val]
    
    id_match = False
    id_format_variant = False
    
    for pid in party_ids:
        if not pid: continue
        for eid in entry_ids:
            if not eid: continue
            if pid == eid:
                id_match = True
                break
            if super_clean_id(pid) == super_clean_id(eid):
                id_format_variant = True
        if id_match:
            break
            
    if id_match:
        score = max(score, 0.99)
        reasons.append("ID_EXACT")
        corroborators += 1
    elif id_format_variant:
        score = max(score, T_REVIEW)
        reasons.append("ID_FORMAT_VARIANT")
        corroborators += 0.5
        
    # DOB
    party_dob = party.get("dob")
    entry_dob = entry.get("dob")
    dob_conflict = False
    if party_dob and entry_dob:
        if isinstance(entry_dob, list):
            e_dob = entry_dob[0]
        else:
            e_dob = entry_dob
            
        if party_dob == e_dob:
            score += 0.1
            reasons.append("DOB_EXACT")
            corroborators += 1
        elif party_dob[:4] == e_dob[:4]:
            score += 0.05
            reasons.append("DOB_YEAR_ONLY")
        else:
            score -= 0.3
            reasons.append("DOB_CONFLICT")
            dob_conflict = True
    elif not party_dob or not entry_dob:
        reasons.append("MISSING_DOB")
        
    # Item 3: Country / Country of Residence
    # Party countries: incorporation/nationality + residence
    p_countries = set()
    if party.get("country"):
        p_countries.add(party.get("country"))
    if party.get("country_of_residence"):
        p_countries.add(party.get("country_of_residence"))
        
    entry_countries = set(entry.get("countries", []))
    if entry.get("country_of_residence"):
        if isinstance(entry.get("country_of_residence"), list):
            entry_countries.update(entry.get("country_of_residence"))
        else:
            entry_countries.add(entry.get("country_of_residence"))
            
    country_conflict = False
    if p_countries and entry_countries:
        if p_countries.intersection(entry_countries):
            score += 0.05
            reasons.append("COUNTRY_RESIDENCE_MATCH")
            corroborators += 1
        else:
            score -= 0.05
            reasons.append("COUNTRY_RESIDENCE_CONFLICT")
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
    elif id_format_variant and tier == "NO_MATCH":
        tier = "REVIEW"
        
    return {
        "score": score,
        "tier": tier,
        "reasons": reasons,
        "matched_alias": matched_alias,
        "party_id": party.get("party_id"),
        "entry_id": entry.get("entry_id")
    }
