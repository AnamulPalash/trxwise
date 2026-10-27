#!/usr/bin/env python3
"""Validate the structural guarantees of the federal training dataset."""

import json
import sys
from collections import Counter
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parents[1] / "data" / "national_services_authority_wise_federal_2000.json"
rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
attack = [row for row in rows if row["attack_event"]]
required_stages = {"initial_access", "endpoint_execution", "process_injection", "c2_beacon", "identity_misuse", "lateral_movement", "data_protection", "critical_service_access", "privileged_resource_access", "residual_c2", "wise_response_plan", "analyst_approval", "customer_response_action", "response_verification", "case_closure"}
expected_source_counts = {
    "trellix:etp": 200, "trellix:ens:exploit": 200, "trellix:edr:event": 200,
    "trellix:nx": 300, "pan:threat": 294, "identity:cloud": 150,
    "WinEventLog:Security": 150, "trellix:dlp:incident": 150,
    "trellix:ips": 150, "federal:application:audit": 200,
    "federal:wise:workflow": 1, "federal:soc:workflow": 3,
    "federal:customer:control": 2,
}

assert len(rows) == 2000, len(rows)
assert all(row.get("synthetic") is True for row in rows)
assert all(row.get("simulation_origin") == "synthetic_training_telemetry" for row in rows)
assert all(rows[index]["timestamp"] <= rows[index + 1]["timestamp"] for index in range(len(rows) - 1))
assert {row["case_id"] for row in attack} == {"FDC-SOC-2026-1027"}
assert required_stages.issubset({row["stage"] for row in attack})
assert len({row["event_id"] for row in rows}) == len(rows)
assert Counter(row["sourcetype"] for row in rows) == expected_source_counts
assert len(attack) == 25, len(attack)
workflow = {row["event_id"]: row for row in attack if row["event_id"] >= "FDC-0000020"}
assert workflow["FDC-0000020"]["stage"] == "wise_response_plan"
assert workflow["FDC-0000020"]["native_telemetry"] is False
assert workflow["FDC-0000021"]["action"] == "approved"
assert workflow["FDC-0000022"]["action"] == "blocked"
assert workflow["FDC-0000023"]["action"] == "session_revoked"
assert workflow["FDC-0000024"]["action"] == "verified"
assert workflow["FDC-0000025"]["action"] == "closed"
print(f"Validated {len(rows)} synthetic events, {len(attack)} linked investigation and workflow events, and exact source-category counts.")
