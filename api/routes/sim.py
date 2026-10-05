from fastapi import APIRouter, HTTPException
import json
import uuid
import time
from typing import Dict, Any

router = APIRouter(prefix="/api/sim", tags=["Simulation"])

scenarios_db = [
    {"id": "S01", "name": "lone_name", "desc": "Add sanctioned Rajeev Malhotra (DOB, country), no ownership edges.", "expected": "PASS"},
    {"id": "S04", "name": "split_30_25", "desc": "Rajeev 30% + sanctioned Sunita 25% of Delta Ltd (30+25=55). Blocked.", "expected": "PASS"},
    {"id": "S05", "name": "exact_50_single", "desc": "Rajeev owns exactly 50%. Show per-regime result OFAC vs EU.", "expected": "PASS"}
]

runs = {}

@router.get("/scenarios")
def list_scenarios():
    return {"scenarios": scenarios_db}

@router.post("/scenario/{scenario_id}/run")
def run_scenario(scenario_id: str):
    run_id = f"SCN-{uuid.uuid4().hex[:8]}"
    
    # Generate fixture steps for the requested scenario
    steps = [
        {"stage": 1, "desc": "Delta received (Rajeev Malhotra)", "elapsed": 10},
        {"stage": 2, "desc": "Names cleaned and match keys built (RJV MLHTR)", "elapsed": 25},
        {"stage": 3, "desc": "Candidates found (1 of 10000)", "elapsed": 30},
        {"stage": 4, "desc": "Scores computed (Score: 1.0, Tier: STRONG)", "elapsed": 45},
        {"stage": 5, "desc": "Ownership rounds (No ownership found)", "elapsed": 50},
        {"stage": 6, "desc": "Alerts created (1 alert)", "elapsed": 60},
        {"stage": 7, "desc": "Result check: PASS", "elapsed": 70, "result": "PASS"}
    ]
    
    if scenario_id == "S04":
        steps[4]["desc"] = "Ownership rounds (Delta Ltd: 30 + 25 = 55 >= 50, blocked)"
        steps[5]["desc"] = "Alerts created (2 alerts)"
    elif scenario_id == "S05":
        steps[4]["desc"] = "Ownership rounds (Exact 50 Ltd: 50 >= 50 (OFAC), 50 > 50 (EU))"
        steps[6]["desc"] = "Result check: PASS (Different outcomes per regime)"
        
    runs[run_id] = {"scenario_id": scenario_id, "steps": steps, "status": "COMPLETED"}
    
    return {"run_id": run_id}

@router.get("/runs/{run_id}/steps")
def get_run_steps(run_id: str):
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"steps": runs[run_id]["steps"]}

@router.post("/runs/{run_id}/reset")
def reset_run(run_id: str):
    if run_id in runs:
        del runs[run_id]
    return {"status": "Reset complete"}
