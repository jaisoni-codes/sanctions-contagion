import pathway as pw

class SanctionDelta(pw.Schema):
    delta_id: str
    list_version: int
    regime: str
    op: str
    entry_id: str
    entity_type: str
    primary_name: str
    aliases: pw.Json
    dob: pw.Json
    countries: pw.Json
    id_numbers: pw.Json
    programs: pw.Json
    event_ts: int
    ingest_ts: int

class PartyChange(pw.Schema):
    change_id: str
    party_id: str
    kind: str
    is_customer: bool
    name: str
    dob: str
    country: str
    id_numbers: pw.Json
    op: str
    event_ts: int
    ingest_ts: int

class EdgeChange(pw.Schema):
    change_id: str
    edge_id: str
    owner_id: str
    owned_id: str
    pct: float
    source_doc: str
    op: str
    event_ts: int
    ingest_ts: int

class Decision(pw.Schema):
    decision_id: str
    alert_id: str
    party_id: str
    entry_id: str
    decision: str
    analyst_id: str
    reason: str
    event_ts: int
