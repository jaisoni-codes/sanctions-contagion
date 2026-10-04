from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/a2a", tags=["agent-to-agent"])

class A2ARequest(BaseModel):
    party_id: str
    context: str

@router.post("/check_party")
def check_party(req: A2ARequest):
    """
    Agent-to-Agent (A2A) endpoint.
    Another system's 'onboarding agent' can call this to get a structured verdict.
    """
    # Mocking response
    return {
        "party_id": req.party_id,
        "verdict": "SAFE",
        "confidence": 0.99,
        "citations": ["No match found in current OFAC/UN lists as of today."],
        "agent_card": {
            "name": "ScreeningAgent",
            "skills": ["screen_party", "explain_alert"]
        }
    }
