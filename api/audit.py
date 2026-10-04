import hashlib
import json
from typing import List, Dict

# In-memory mock for Postgres append-only audit_log table
AUDIT_LOG = []

def canonical_json(payload: dict) -> str:
    """Returns a deterministic JSON string for hashing."""
    return json.dumps(payload, sort_keys=True, separators=(',', ':'))

def append_audit_event(actor: str, event_type: str, party_id: str, payload: dict):
    """
    Appends an event to the hash-chained audit log.
    hash = sha256(prev_hash + canonical_json(payload))
    """
    prev_hash = "0" * 64
    if AUDIT_LOG:
        prev_hash = AUDIT_LOG[-1]["hash"]
        
    payload_str = canonical_json(payload)
    data_to_hash = prev_hash + payload_str
    
    current_hash = hashlib.sha256(data_to_hash.encode('utf-8')).hexdigest()
    
    event = {
        "seq": len(AUDIT_LOG) + 1,
        "actor": actor,
        "event_type": event_type,
        "party_id": party_id,
        "payload": payload,
        "prev_hash": prev_hash,
        "hash": current_hash
    }
    AUDIT_LOG.append(event)
    return event

def verify_audit_chain() -> bool:
    """Verifies the integrity of the hash chain."""
    expected_prev = "0" * 64
    for event in AUDIT_LOG:
        if event["prev_hash"] != expected_prev:
            return False
            
        payload_str = canonical_json(event["payload"])
        data_to_hash = expected_prev + payload_str
        expected_hash = hashlib.sha256(data_to_hash.encode('utf-8')).hexdigest()
        
        if event["hash"] != expected_hash:
            return False
            
        expected_prev = event["hash"]
        
    return True

def query_as_of(party_id: str, as_of_seq: int) -> List[Dict]:
    """Reconstructs decisions for a party up to a given sequence point."""
    history = []
    for event in AUDIT_LOG:
        if event["seq"] > as_of_seq:
            break
        if event["party_id"] == party_id:
            history.append(event)
    return history
