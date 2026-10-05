from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

class DecisionModel(BaseModel):
    decision: str
    reason: str
    expected_version: Optional[int] = None

# Demo Scenario Fixtures (Raju Mehra, Ownership chains, etc.)
ALERTS_DB = {
    "alert_raju": {
        "id": "alert_raju",
        "party_id": "CUST_RAJU_01",
        "party_name": "Raju Mehra",
        "regime": "OFAC",
        "tier": "STRONG",
        "score": 0.98,
        "status": "OPEN",
        "time_to_flag_ms": 42,
        "is_retracted": False
    },
    "alert_mehra_holdings": {
        "id": "alert_mehra_holdings",
        "party_id": "COMP_MEHRA_HLD",
        "party_name": "Mehra Holdings",
        "regime": "OFAC",
        "tier": "OWNERSHIP",
        "score": 1.0,
        "status": "OPEN",
        "time_to_flag_ms": 115,
        "is_retracted": False,
        "ownership_detail": "Raju Mehra holds 60%"
    },
    "alert_coastal": {
        "id": "alert_coastal",
        "party_id": "COMP_COASTAL",
        "party_name": "Coastal Freight Ltd",
        "regime": "OFAC",
        "tier": "OWNERSHIP",
        "score": 1.0,
        "status": "OPEN",
        "time_to_flag_ms": 130,
        "is_retracted": False,
        "ownership_detail": "Mehra Holdings holds 55%"
    },
    "alert_agg": {
        "id": "alert_agg",
        "party_id": "COMP_AGG_TEST",
        "party_name": "Aggregated Logistics",
        "regime": "UN",
        "tier": "OWNERSHIP",
        "score": 1.0,
        "status": "OPEN",
        "time_to_flag_ms": 85,
        "is_retracted": False,
        "ownership_detail": "Blocked Owner A (30%) + Blocked Owner B (25%) >= 50%"
    },
    "alert_homonym": {
        "id": "alert_homonym",
        "party_id": "CUST_RAJU_02",
        "party_name": "Raju Mehra (Homonym)",
        "regime": "OFAC",
        "tier": "DISCOUNTED",
        "score": 0.85,
        "status": "CLOSED",
        "time_to_flag_ms": 40,
        "is_retracted": False,
        "reason": "DOB_CONFLICT"
    },
    "alert_common": {
        "id": "alert_common",
        "party_id": "CUST_COMMON",
        "party_name": "Rahul Sharma",
        "regime": "EU",
        "tier": "REVIEW",
        "score": 0.88,
        "status": "OPEN",
        "time_to_flag_ms": 38,
        "is_retracted": False,
        "reason": "COMMON_NAME_NO_CORROBORATOR"
    },
    "alert_retracted": {
        "id": "alert_retracted",
        "party_id": "COMP_OLD",
        "party_name": "Old Holdings",
        "regime": "UK",
        "tier": "OWNERSHIP",
        "score": 1.0,
        "status": "RETRACTED",
        "time_to_flag_ms": 150,
        "is_retracted": True,
        "reason": "Edge deleted or owner delisted"
    },
    "alert_release_review": {
        "id": "alert_release_review",
        "party_id": "COMP_PREV_BLOCKED",
        "party_name": "Previously Blocked Corp",
        "regime": "OFAC",
        "tier": "STRONG",
        "score": 0.99,
        "status": "RELEASE_REVIEW",
        "time_to_flag_ms": 90,
        "is_retracted": False,
        "reason": "Support disappeared, manual release required"
    }
}

@router.get("")
def list_alerts():
    return list(ALERTS_DB.values())

@router.get("/{alert_id}")
def get_alert(alert_id: str):
    alert = ALERTS_DB.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/{alert_id}/decision")
def make_decision(alert_id: str, decision: DecisionModel):
    alert = ALERTS_DB.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if decision.decision == "CONFIRM":
        alert["status"] = "CONFIRMED_BLOCK"
    elif decision.decision == "REJECT":
        alert["status"] = "REJECTED_CLEAR"
    elif decision.decision == "ESCALATE":
        alert["status"] = "ESCALATED"
    else:
        raise HTTPException(status_code=400, detail="Invalid decision")
        
    return {"status": "success", "alert": alert}

import uuid

# Store unread notifications
external_notifications = []

class ExternalPushModel(BaseModel):
    name: str
    scenario_id: str
    tier: str = "STRONG"
    description: str = ""

@router.post("/external-push")
def external_push(data: ExternalPushModel):
    new_alert_id = f"EXT-{uuid.uuid4().hex[:6]}"
    
    # Create the alert in DB
    ALERTS_DB[new_alert_id] = {
        "id": new_alert_id,
        "party_id": f"EXT_PARTY_{new_alert_id}",
        "party_name": data.name,
        "regime": "OFAC",
        "tier": data.tier,
        "score": 0.95,
        "status": "OPEN",
        "time_to_flag_ms": 30,
        "is_retracted": False,
        "reason": data.description or "External match pushed"
    }
    
    notif = {
        "alert_id": new_alert_id,
        "name": data.name,
        "scenario_id": data.scenario_id,
        "tier": data.tier,
        "timestamp": "Just now"
    }
    external_notifications.append(notif)
    return {"status": "success", "alert_id": new_alert_id}

@router.get("/latest-external")
def get_latest_external():
    # Return all unread and clear them
    res = list(external_notifications)
    external_notifications.clear()
    return res
