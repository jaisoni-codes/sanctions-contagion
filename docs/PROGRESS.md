# Project Progress

## Phases & Acceptance Criteria

- [x] **Phase 0: Skeleton**
  - **Deliverables**: Repo, compose, Makefile, seed generator with ground truth, engine reading sanctions and parties and writing to Postgres, API health, web shell with auth.
  - **Acceptance**: `make demo` shows dashboard with live counts; seed is deterministic.

- [x] **Phase 1: Direct matching**
  - **Deliverables**: Normalize, blocking, scoring, tiers, reason codes, alert upsert and retraction, latency stamps, golden-table tests.
  - **Acceptance**: Injecting a fictional entry produces expected STRONG and REVIEW alerts; homonyms DISCOUNTED; p95 latency measured.

- [x] **Phase 2: Ownership contagion**
  - **Deliverables**: Fixpoint or unrolled joins, per-regime rules, provenance, graph API, reference-implementation property tests.
  - **Acceptance**: All TP-CHAIN, TP-AGG, TP-CYCLE, TN-NEAR cases correct; delist and edge change retract correctly.

- [x] **Phase 3: Analyst console**
  - **Deliverables**: Command Center, Alert Queue and Detail, Ownership Explorer, decisions fed back to engine, WebSocket live updates, four-eyes.
  - **Acceptance**: Approve and reject work end to end; rejection retracts dependent chain; UI updates without refresh.

- [x] **Phase 4: Audit and resilience**
  - **Deliverables**: Hash-chained audit, as-of query, persistence, crash drill, kill switch modes, RBAC.
  - **Acceptance**: Crash drill passes; 'why cleared on 15 March' answered from audit; verify button works.

- [x] **Phase 5: LLM, RAG, agents**
  - **Deliverables**: Explainer with validator and fallback, policy index, copilot with tool trace, MCP server, guardrail tests.
  - **Acceptance**: Hallucination and timeout drills pass; citations resolve; MCP tools callable by an external client.

- [x] **Phase 6: Evaluation and polish**
  - **Deliverables**: Eval harness, batch baselines, metrics and observability pages, parity, load tests, docs, demo script automation, recorded video.
  - **Acceptance**: `make eval` produces all charts; E2E replays the demo; README works on a clean machine.

- [x] **Phase 7: Stretch**
  - **Deliverables**: Calibrator, A2A demo, SAR draft, adverse media, Kafka input.
  - **Acceptance**: Only if phases 0 to 6 are green.

## Repository Layout

```text
sanctions-contagion/
  README.md Makefile docker-compose.yml .env.example LICENSE
  docs/
    architecture.md DECISIONS.md runbook.md evaluation.md bdh-future.md
    policies/ (live policy folder) diagrams/
  config/
    thresholds.yaml weights.yaml ownership_rules.yaml aliases.yaml roles.yaml
  engine/
    pipeline.py schemas.py connectors/ (sanctions_feed.py, rest_inputs.py)
    matching/ (normalize.py, blocking.py, score.py) ownership.py alerts.py
    actions.py llm/ (explain.py, validate.py, templates.py, agent.py, tools.py)
    mcp_server.py policy_index.py metrics.py sinks/ (postgres.py, events.py)
  api/
    main.py auth.py routes/ services/ models.py ws.py audit.py sim.py
  web/
    src/ (pages, components, hooks, api, store) e2e/
  tools/seed/
    generate.py ground_truth.json fictional_entries.jsonl scenarios/*.yaml
  eval/
    run_latency.py run_accuracy.py run_batch_baseline.py run_retrieval.py parity.py
  tests/
    unit/ scenario/ integration/
  data/
    seed/ stream/ state/ (gitignored: state)
```
