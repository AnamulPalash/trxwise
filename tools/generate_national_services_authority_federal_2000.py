#!/usr/bin/env python3
"""Create a deterministic, fictional 2,000-event federal SOC training dataset.

The generated file contains only inert, synthetic records. It does not contact a
network service, execute a payload, or represent vendor-native telemetry.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUTPUT = Path(__file__).parents[1] / "data" / "national_services_authority_wise_federal_2000.json"
CASE_ID = "FDC-SOC-2026-1027"
SCENARIO = "synthetic_national_services_authority_federal_training"
RNG = random.Random(20261027)
START = datetime(2026, 10, 20, 7, 0, tzinfo=timezone.utc)
ATTACK_START = datetime(2026, 10, 27, 5, 45, tzinfo=timezone.utc)

SOURCES = [
    ("trellix:etp", "Trellix", "Email Protection", 200),
    ("trellix:ens:exploit", "Trellix", "Endpoint Security", 200),
    ("trellix:edr:event", "Trellix", "Endpoint Detection and Response", 200),
    ("trellix:nx", "Trellix", "Network Security NX", 300),
    ("pan:threat", "Palo Alto Networks", "PAN-OS NGFW", 294),
    ("identity:cloud", "Identity Provider", "Identity Cloud", 150),
    ("WinEventLog:Security", "Microsoft", "Windows Security", 150),
    ("trellix:dlp:incident", "Trellix", "Data Loss Prevention", 150),
    ("trellix:ips", "Trellix", "Network Security Platform IPS", 150),
    ("federal:application:audit", "National Services Authority", "Citizen Services Application Audit", 200),
    ("federal:wise:workflow", "Trellix", "Trellix Wise (simulated workflow)", 1),
    ("federal:soc:workflow", "National Services Authority", "Federal SOC Workflow (simulated)", 3),
    ("federal:customer:control", "National Services Authority", "Customer Control Workflow (simulated)", 2),
]

USERS = ["alex.rivera", "jamie.chen", "morgan.taylor", "priya.shah", "lee.wong"]
HOSTS = ["NSA-USER-047", "NSA-USER-118", "NSA-APP-02", "NSA-API-01", "NSA-JUMP-01"]


def iso(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def base_event(event_id: int, timestamp: datetime, sourcetype: str, vendor: str, product: str) -> dict:
    return {
        "timestamp": iso(timestamp),
        "event_id": f"FDC-{event_id:07d}",
        "scenario": SCENARIO,
        "simulation_origin": "synthetic_training_telemetry",
        "synthetic": True,
        "attack_event": False,
        "sourcetype": sourcetype,
        "vendor": vendor,
        "product": product,
        "source_system": product,
        "severity": "informational",
        "event_type": "activity",
    }


def benign_event(event_id: int, timestamp: datetime, sourcetype: str, vendor: str, product: str) -> dict:
    event = base_event(event_id, timestamp, sourcetype, vendor, product)
    user = RNG.choice(USERS)
    host = RNG.choice(HOSTS)
    event.update({"user": f"{user}@national-services.example", "src_host": host, "src_ip": f"10.42.{RNG.randint(10, 30)}.{RNG.randint(10, 240)}"})
    if sourcetype == "trellix:etp":
        event.update({"event_type": "email", "sender": "notices@partner.example", "recipient": event["user"], "subject": "Routine service update", "action": "delivered", "verdict": "clean"})
    elif sourcetype in {"trellix:ens:exploit", "trellix:edr:event"}:
        event.update({"event_type": "endpoint", "process_name": "msedge.exe", "process_id": RNG.randint(1000, 9000), "action": "observed", "signature": "Normal endpoint activity"})
    elif sourcetype in {"trellix:nx", "pan:threat", "trellix:ips"}:
        event.update({"event_type": "network", "dest_ip": "198.51.100.24", "dest_port": 443, "transport": "tcp", "app": "ssl", "action": "allowed", "signature": "Normal encrypted session"})
    elif sourcetype == "identity:cloud":
        event.update({"event_type": "authentication", "authentication_method": "password+mfa", "mfa_status": "satisfied", "device_trust": "managed", "action": "success"})
    elif sourcetype == "WinEventLog:Security":
        event.update({"event_type": "logon", "EventCode": 4624, "logon_type": 2, "action": "success"})
    elif sourcetype == "trellix:dlp:incident":
        event.update({"event_type": "data_policy", "file_name": "service_delivery_notes.docx", "file_classification": "OFFICIAL", "policy_id": "DLP-OFFICIAL-ALLOW", "action": "allowed"})
    else:
        event.update({"event_type": "application_audit", "application": "Citizen Services Portal", "action": "normal_access", "resource": "case-summary"})
    return event


def attack(event_id: int, offset_seconds: int, sourcetype: str, vendor: str, product: str, stage: str, severity: str, **fields: object) -> dict:
    event = base_event(event_id, ATTACK_START + timedelta(seconds=offset_seconds), sourcetype, vendor, product)
    event.update({"case_id": CASE_ID, "attack_event": True, "stage": stage, "severity": severity})
    event.update(fields)
    return event


def attack_events() -> list[dict]:
    e = []
    add = e.append
    add(attack(1, 0, "trellix:etp", "Trellix", "Email Protection", "initial_access", "high", event_type="email", sender="vendor-services@federal-training.example", recipient="alex.rivera@national-services.example", subject="Action required: service delivery schedule", message_id="FDC-MSG-1027-01", file_name="Service_Delivery_Schedule.xlsm", file_hash="federal-training-sha256-01", verdict="suspicious", action="delivered", mitre_technique_id="T1566.001"))
    add(attack(2, 8, "trellix:etp", "Trellix", "Email Protection", "initial_access", "medium", event_type="email", sender="vendor-services@federal-training.example", recipient="jamie.chen@national-services.example", subject="Action required: service delivery schedule", message_id="FDC-MSG-1027-02", file_name="Service_Delivery_Schedule.xlsm", file_hash="federal-training-sha256-01", verdict="suspicious", action="quarantined", mitre_technique_id="T1566.001"))
    add(attack(3, 16, "trellix:etp", "Trellix", "Email Protection", "initial_access", "medium", event_type="email", sender="vendor-services@federal-training.example", recipient="priya.shah@national-services.example", subject="Action required: service delivery schedule", message_id="FDC-MSG-1027-03", file_name="Service_Delivery_Schedule.xlsm", file_hash="federal-training-sha256-01", verdict="suspicious", action="quarantined", mitre_technique_id="T1566.001"))
    add(attack(4, 42, "trellix:ens:exploit", "Trellix", "Endpoint Security", "endpoint_execution", "high", event_type="alert", user="alex.rivera@national-services.example", workstation="NSA-USER-047", parent_process_name="EXCEL.EXE", process_name="powershell.exe", process_id=4128, process_guid="FDC-PROC-1027-01", process_command_line="[INERT_FEDERAL_TRAINING_COMMAND]", signature="Suspicious Office child process", action="alerted", mitre_technique_id="T1059.001"))
    add(attack(5, 55, "trellix:edr:event", "Trellix", "Endpoint Detection and Response", "endpoint_execution", "high", event_type="alert", user="alex.rivera@national-services.example", workstation="NSA-USER-047", parent_process_name="EXCEL.EXE", process_name="powershell.exe", process_id=4128, process_guid="FDC-PROC-1027-01", process_command_line="[INERT_FEDERAL_TRAINING_COMMAND]", signature="PowerShell execution observed", action="alerted", mitre_technique_id="T1059.001"))
    add(attack(6, 70, "trellix:edr:event", "Trellix", "Endpoint Detection and Response", "process_injection", "critical", event_type="alert", user="alex.rivera@national-services.example", workstation="NSA-USER-047", process_name="powershell.exe", target_process="svchost.exe", process_guid="FDC-PROC-1027-01", signature="Synthetic process injection indicator", action="alerted", mitre_technique_id="T1055.002"))
    add(attack(7, 92, "trellix:nx", "Trellix", "Network Security NX", "c2_beacon", "high", event_type="alert", src_host="NSA-USER-047", src_ip="10.42.20.47", dest="c2.federal-training.example", dest_ip="203.0.113.77", dest_port=8443, transport="tcp", app="ssl", session_id="FDC-NX-1027-01", ja3_hash="FDC-TRAINING-JA3", bytes_sent=1842, bytes_received=3291, signature="Periodic encrypted beacon pattern", action="alerted", mitre_technique_id="T1071.001"))
    add(attack(8, 118, "pan:threat", "Palo Alto Networks", "PAN-OS NGFW", "c2_beacon", "high", event_type="network", src_host="NSA-USER-047", src_ip="10.42.20.47", dest_ip="203.0.113.77", dest_port=8443, src_zone="Federal-User", dest_zone="Training-Internet", rule="USER-EGRESS", session_id="FDC-PAN-1027-01", bytes_out=1842, bytes_in=3291, signature="Suspicious beacon correlation", action="allowed", mitre_technique_id="T1071.001"))
    add(attack(9, 146, "trellix:nx", "Trellix", "Network Security NX", "c2_beacon", "high", event_type="alert", src_host="NSA-USER-047", src_ip="10.42.20.47", dest="c2.federal-training.example", dest_ip="203.0.113.77", dest_port=8443, transport="tcp", app="ssl", session_id="FDC-NX-1027-02", bytes_sent=2024, bytes_received=3408, signature="Repeated encrypted beacon pattern", action="alerted", mitre_technique_id="T1071.001"))
    add(attack(10, 170, "identity:cloud", "Identity Provider", "Identity Cloud", "identity_misuse", "high", event_type="authentication", user="alex.rivera@national-services.example", src_ip="198.51.100.197", device_trust="untrusted", authentication_method="session_reuse", mfa_status="not_challenged", session_id="FDC-ID-1027-01", application="Privileged Access Gateway", action="success", signature="Session reuse from untrusted device", mitre_technique_id="T1550.004"))
    add(attack(11, 185, "identity:cloud", "Identity Provider", "Identity Cloud", "identity_misuse", "high", event_type="authentication", user="alex.rivera@national-services.example", src_ip="198.51.100.197", device_trust="untrusted", authentication_method="session_reuse", mfa_status="not_challenged", session_id="FDC-ID-1027-01", application="Privileged Access Gateway", action="risk_recorded", signature="Missing expected MFA challenge", mitre_technique_id="T1550.004"))
    add(attack(12, 210, "WinEventLog:Security", "Microsoft", "Windows Security", "lateral_movement", "high", event_type="logon", user="NATIONAL\\alex.rivera", src_host="NSA-USER-047", src_ip="10.42.20.47", dest_host="NSA-JUMP-01", dest_ip="10.42.10.15", EventCode=4624, logon_type=10, authentication_package="Negotiate", action="success", mitre_technique_id="T1021.001"))
    add(attack(13, 225, "trellix:edr:event", "Trellix", "Endpoint Detection and Response", "lateral_movement", "high", event_type="alert", user="alex.rivera@national-services.example", workstation="NSA-JUMP-01", src_ip="10.42.20.47", signature="Remote command activity after RDP logon", action="alerted", mitre_technique_id="T1021.001"))
    add(attack(14, 250, "trellix:dlp:incident", "Trellix", "Data Loss Prevention", "data_protection", "high", event_type="data_policy", user="alex.rivera@national-services.example", workstation="NSA-JUMP-01", file_name="Citizen_Services_Eligibility_Extract.csv", file_size=1843200, file_classification="OFFICIAL:Sensitive", policy_id="DLP-CITIZEN-DATA-EXTERNAL", destination_target="c2.federal-training.example", action="blocked", signature="Sensitive citizen-data transfer blocked", mitre_technique_id="T1041"))
    add(attack(15, 268, "trellix:dlp:incident", "Trellix", "Data Loss Prevention", "data_protection", "high", event_type="data_policy", user="alex.rivera@national-services.example", workstation="NSA-JUMP-01", file_name="Service_Continuity_Contacts.xlsx", file_size=625000, file_classification="PROTECTED", policy_id="DLP-CITIZEN-DATA-EXTERNAL", destination_target="c2.federal-training.example", action="blocked", signature="Protected document transfer blocked", mitre_technique_id="T1041"))
    add(attack(16, 300, "trellix:ips", "Trellix", "Network Security Platform IPS", "critical_service_access", "critical", event_type="alert", src_host="NSA-JUMP-01", src_ip="10.42.10.15", dest_host="NSA-API-01", dest_ip="10.42.60.20", dest_port=443, src_zone="Privileged-Access", dest_zone="Protected-Services", signature_id="FDC-IPS-41721", signature="Unexpected privileged route to protected service", action="alerted", mitre_technique_id="T1021.001"))
    add(attack(17, 318, "federal:application:audit", "National Services Authority", "Citizen Services Application Audit", "critical_service_access", "critical", event_type="application_audit", user="alex.rivera@national-services.example", src_host="NSA-JUMP-01", application="Citizen Services Portal", resource="eligibility-records", action="denied", reason="Privileged support account has no approved case assignment", audit_id="FDC-APP-1027-01", mitre_technique_id="T1078"))
    add(attack(18, 345, "federal:application:audit", "National Services Authority", "Citizen Services Application Audit", "privileged_resource_access", "critical", event_type="application_audit", user="alex.rivera@national-services.example", src_host="NSA-JUMP-01", application="Citizen Services Portal", resource="bulk-record-export", action="denied", reason="Access pattern exceeds authorised role", audit_id="FDC-APP-1027-02", mitre_technique_id="T1078"))
    add(attack(19, 372, "trellix:nx", "Trellix", "Network Security NX", "residual_c2", "high", event_type="alert", src_host="NSA-JUMP-01", src_ip="10.42.10.15", dest="c2.federal-training.example", dest_ip="203.0.113.77", dest_port=8443, transport="tcp", app="ssl", session_id="FDC-NX-1027-03", signature="Related encrypted beacon after lateral movement", action="alerted", mitre_technique_id="T1071.001"))
    add(attack(20, 400, "federal:wise:workflow", "Trellix", "Trellix Wise (simulated workflow)", "wise_response_plan", "high", event_type="response_plan", source_system="Simulation workflow", native_telemetry=False, recommendation_id="FDC-WISE-PLAN-1027-01", evidence_event_ids=["FDC-0000004", "FDC-0000007", "FDC-0000010", "FDC-0000012", "FDC-0000019"], confidence="high", uncertainty="Validate ownership of the reused identity session before disabling access.", recommended_actions=["Block the identified C2 destination at the customer network control", "Revoke the named synthetic identity session", "Preserve source records for analyst review"], action="recommended"))
    add(attack(21, 430, "federal:soc:workflow", "National Services Authority", "Federal SOC Workflow (simulated)", "analyst_approval", "high", event_type="approval", source_system="Simulation workflow", native_telemetry=False, approval_id="FDC-APPROVAL-1027-01", approver_role="Federal SOC analyst", decision="approved", evidence_event_ids=["FDC-0000020"], approved_action_ids=["FDC-RESPONSE-1027-01", "FDC-RESPONSE-1027-02"], rationale="Evidence supports bounded customer actions while the identity ownership question remains tracked.", action="approved"))
    add(attack(22, 455, "federal:customer:control", "National Services Authority", "Customer Control Workflow (simulated)", "customer_response_action", "high", event_type="control_action", source_system="Customer network egress control (simulated)", native_telemetry=False, response_action_id="FDC-RESPONSE-1027-01", approval_id="FDC-APPROVAL-1027-01", change_ticket="FDC-CHG-1027-01", control_id="FED-NET-EGRESS-01", src_host="NSA-JUMP-01", src_ip="10.42.10.15", dest_ip="203.0.113.77", dest_port=8443, action_scope="Block the identified synthetic C2 destination", action="blocked", reason="Authorised response to FDC-SOC-2026-1027"))
    add(attack(23, 470, "federal:customer:control", "National Services Authority", "Customer Control Workflow (simulated)", "customer_response_action", "high", event_type="control_action", source_system="Customer identity control (simulated)", native_telemetry=False, response_action_id="FDC-RESPONSE-1027-02", approval_id="FDC-APPROVAL-1027-01", change_ticket="FDC-CHG-1027-01", control_id="FED-ID-SESSION-01", user="alex.rivera@national-services.example", session_id="FDC-ID-1027-01", action_scope="Revoke the named synthetic identity session", action="session_revoked", reason="Authorised response to FDC-SOC-2026-1027"))
    add(attack(24, 510, "federal:soc:workflow", "National Services Authority", "Federal SOC Workflow (simulated)", "response_verification", "medium", event_type="verification", source_system="Simulation workflow", native_telemetry=False, verification_id="FDC-VERIFY-1027-01", evidence_event_ids=["FDC-0000019", "FDC-0000022", "FDC-0000023"], observation_window_minutes=15, verification_result="No further synthetic C2 event is recorded after the authorised block in this exercise window.", action="verified"))
    add(attack(25, 540, "federal:soc:workflow", "National Services Authority", "Federal SOC Workflow (simulated)", "case_closure", "informational", event_type="case_management", source_system="Simulation workflow", native_telemetry=False, closure_id="FDC-CLOSE-1027-01", case_status="closed_for_training", closure_reason="Synthetic response actions recorded and verification completed.", retained_hunt_question="Search the lab for the same synthetic file hash, command marker and C2 destination.", action="closed"))
    return e


def main() -> None:
    attack_rows = attack_events()
    background = []
    event_id = 100001
    attack_by_source = {}
    for row in attack_rows:
        attack_by_source[row["sourcetype"]] = attack_by_source.get(row["sourcetype"], 0) + 1
    for source in SOURCES:
        sourcetype, vendor, product, expected_total = source
        background_total = expected_total - attack_by_source.get(sourcetype, 0)
        for _ in range(background_total):
            timestamp = START + timedelta(seconds=RNG.randint(0, int((ATTACK_START - START).total_seconds() - 600)))
            background.append(benign_event(event_id, timestamp, sourcetype, vendor, product))
            event_id += 1
    rows = sorted(background + attack_rows, key=lambda row: (row["timestamp"], row["event_id"]))
    if len(rows) != 2000:
        raise RuntimeError(f"Expected 2000 events, generated {len(rows)}")
    if sum(row.get("attack_event", False) for row in rows) != len(attack_rows):
        raise RuntimeError("Attack-event count check failed")
    OUTPUT.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(rows)} events and {len(attack_rows)} correlated attack events.")


if __name__ == "__main__":
    main()
