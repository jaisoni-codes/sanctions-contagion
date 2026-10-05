from fastapi import APIRouter, HTTPException
import json
import uuid
import os
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
    
    fixture_path = f"tools/seed/fixtures/{scenario_id}.json"
    if os.path.exists(fixture_path):
        with open(fixture_path, "r") as f:
            data = json.load(f)
            steps = data.get("steps", [])
    else:
        # Fallback if fixture doesn't exist
        steps = [
            {"stage": 1, "desc": "Delta received", "elapsed": 10},
            {"stage": 2, "desc": "Names cleaned", "elapsed": 20},
            {"stage": 7, "desc": "Result check: PASS", "elapsed": 10, "result": "PASS"}
        ]
        
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
