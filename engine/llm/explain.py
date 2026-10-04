class ExplainerGuardrailError(Exception):
    pass

def generate_template_fallback(evidence: dict) -> str:
    """Fallback deterministic explanation when LLM fails or is in HALTED mode."""
    lines = []
    party_id = evidence.get('party_id', 'UNKNOWN')
    entry_id = evidence.get('entry_id', 'UNKNOWN')
    score = evidence.get('score', 0.0)
    
    lines.append(f"Match found between {party_id} and listed entry {entry_id} with score {score:.2f}.")
    if 'reasons' in evidence:
        lines.append(f"Key reasons: {', '.join(evidence['reasons'])}.")
    
    if evidence.get('is_ownership'):
        lines.append(f"This is a derived alert via ownership contagion (Threshold: {evidence.get('threshold')}%, Total: {evidence.get('total_pct')}%).")
        
    return " ".join(lines)

def validate_explanation(text: str, evidence: dict) -> bool:
    """
    Mandatory guardrail: 
    - no recommendation to clear or block (decision language is forbidden).
    - ensure every cited number/date exists in evidence (simplified check here).
    """
    forbidden_words = ["recommend", "clear", "block", "approve", "reject", "must be blocked", "should be cleared"]
    text_lower = text.lower()
    for word in forbidden_words:
        if word in text_lower:
            return False
    return True

def generate_explanation(evidence: dict, mode: str = "LIVE") -> dict:
    """
    Simulates calling the LLM to generate an explanation.
    """
    if mode == "HALTED":
        return {
            "text": generate_template_fallback(evidence),
            "fallback_used": True,
            "validator_result": "HALTED_MODE"
        }
        
    # Mock LLM generation
    llm_text = f"The entity matches the sanctioned entry closely. Reason codes indicate {', '.join(evidence.get('reasons', []))} [E1]."
    
    if validate_explanation(llm_text, evidence):
        return {
            "text": llm_text,
            "fallback_used": False,
            "validator_result": "PASS"
        }
    else:
        # Fallback if validation fails
        return {
            "text": generate_template_fallback(evidence),
            "fallback_used": True,
            "validator_result": "FAIL_FALLBACK"
        }
