from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/control", tags=["control"])

class ModeUpdate(BaseModel):
    mode: str
    reason: str

# System state mock
SYSTEM_STATE = {
    "mode": "LIVE",
    "changed_by": "system",
    "reason": "startup"
}

# Mock RBAC dependency
def require_admin(user_role: str = "admin"):
    if user_role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user_role

@router.get("/mode")
def get_mode():
    return SYSTEM_STATE

@router.post("/mode")
def set_mode(update: ModeUpdate, role: str = Depends(require_admin)):
    valid_modes = {"LIVE", "SHADOW", "HALTED"}
    if update.mode not in valid_modes:
        raise HTTPException(status_code=400, detail="Invalid mode")
        
    SYSTEM_STATE["mode"] = update.mode
    SYSTEM_STATE["reason"] = update.reason
    SYSTEM_STATE["changed_by"] = "admin_user" # mocked
    
    # In a real scenario, this would write to Postgres and the Engine would read it
    from api.audit import append_audit_event
    append_audit_event("admin_user", "MODE_CHANGED", "SYSTEM", {"mode": update.mode, "reason": update.reason})
    
    return SYSTEM_STATE
