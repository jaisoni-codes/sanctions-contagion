from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import alerts, control, a2a, sim
from api.ws import router as ws_router
from api.audit import verify_audit_chain

app = FastAPI(title="Sanctions Contagion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts.router)
app.include_router(control.router)
app.include_router(a2a.router)
app.include_router(sim.router)
app.include_router(ws_router)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/api/overview")
def overview():
    # ALL values returned here must be dynamic in the real engine.
    # For Phase 3/5 mock, we return the exact structure the UI needs.
    return {
        "customers": 10000,
        "companies": 3000,
        "mode": "LIVE",
        "system_health": {
            "status": "nominal",
            "message": "All Systems Nominal",
            "engine_heartbeat": "ok",
            "sink_errors": 0
        },
        "open_alerts_by_tier": {
            "STRONG": 2,
            "OWNERSHIP": 3,
            "REVIEW": 1
        },
        "lists_freshness": {
            "OFAC": {"status": "fresh", "age_mins": 2},
            "UN": {"status": "fresh", "age_mins": 5},
            "EU": {"status": "stale", "age_mins": 145},
            "UK": {"status": "fresh", "age_mins": 10}
        },
        "latency": {
            "p50_ms": 45,
            "p95_ms": 120
        },
        "throughput_eps": 450
    }

@app.get("/api/audit/verify")
def verify_audit():
    is_valid = verify_audit_chain()
    return {"valid": is_valid}
