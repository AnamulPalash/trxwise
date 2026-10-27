# National Services Authority: Federal SOC training dataset

This repository contains a **fictional, synthetic** 2,000-event dataset for a
Trellix Wise and Splunk lab. It models a federal-department SOC investigation,
not an actual government department or vendor export.

## Scenario

Case `FDC-SOC-2026-1027` follows a phishing email to a user workstation,
inert PowerShell telemetry, synthetic process-injection indicators, C2-like
network records, session-reuse evidence, lateral movement to a privileged jump
host, blocked data transfer, and denied access to a protected citizen-services
application. The final workflow records the synthetic Wise response plan,
analyst approval, customer-owned action, verification and case closure.

- 2,000 NDJSON records, one object per line
- 25 linked investigation and workflow events across 13 source categories:
  ten simulated security telemetry categories and three simulated workflow
  categories
- Every record includes `synthetic: true` and
  `simulation_origin: synthetic_training_telemetry`
- No payloads, live credentials, real IPs, real government data, or external
  network actions are included

## Response and governance evidence

The final six records make the simulation's response sequence inspectable.
They are deliberately marked `native_telemetry: false`: they are fictional
workflow records, not vendor-native Wise, SOC or control telemetry.

| Event IDs | Stage | What the record demonstrates |
| --- | --- | --- |
| `FDC-0000020` | `wise_response_plan` | A synthetic, source-linked Wise response recommendation with evidence IDs, confidence and an explicit uncertainty. |
| `FDC-0000021` | `analyst_approval` | A fictional federal SOC analyst approval, including approved action IDs and rationale. |
| `FDC-0000022` to `FDC-0000023` | `customer_response_action` | Fictional customer-owned network block and identity-session revocation records, each tied to the approval and change ticket. |
| `FDC-0000024` | `response_verification` | A synthetic verification result and its evidence basis. |
| `FDC-0000025` | `case_closure` | A training-only closure record with the retained hunt question. |

## Import with Splunk Web, no HEC required

1. On the lab Windows endpoint, run:

   ```powershell
   Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/AnamulPalash/trxwise/main/tools/download_national_services_authority_federal_2000.ps1' -OutFile '.\download_national_services_authority_federal_2000.ps1'
   .\download_national_services_authority_federal_2000.ps1
   ```

2. In Splunk, go to **Settings > Add Data > Upload** and upload
   `national_services_authority_wise_federal_latest.json`.
3. Select `_json`, make sure Splunk uses field `timestamp`, format
   `%Y-%m-%dT%H:%M:%SZ`, and timezone UTC.
4. Use a new Events index such as `federal_wise`. If you must use the existing
   `services_narnia` lab index, keep the `case_id` filter in every search.

A one-file upload assigns one Splunk metadata sourcetype to every record. The
event's `sourcetype` JSON field still supports search-time correlation, but it
does not create per-event Splunk metadata sourcetypes.

## Validation SPL

```spl
index=federal_wise earliest=0
| stats count as total dc(sourcetype) as source_categories values(synthetic) as synthetic_flags
```

Expected: `total=2000`, `source_categories=13`, `synthetic_flags=true`.

```spl
index=federal_wise earliest=0 case_id="FDC-SOC-2026-1027"
| sort 0 _time
| table _time event_id stage product severity user src_host dest_host src_ip dest_ip action signature mitre_technique_id
```

```spl
index=federal_wise earliest=0 case_id="FDC-SOC-2026-1027" dest_ip="203.0.113.77"
| stats count values(stage) as stages values(src_host) as affected_hosts by dest_ip dest_port
```

```spl
index=federal_wise earliest=0 case_id="FDC-SOC-2026-1027" action="blocked"
| table _time stage product file_name resource action reason
```

```spl
index=federal_wise earliest=0 case_id="FDC-SOC-2026-1027"
stage IN ("wise_response_plan", "analyst_approval", "customer_response_action", "response_verification", "case_closure")
| table _time event_id stage source_system action approval_id response_action_id evidence_event_ids reason verification_result case_status
```

## Wise lab boundary

Configure the installed Splunk connector only with its supported Ingest and/or
Enrich features and read-only credentials. A successful connection test does
not prove index polling, alert eligibility, enrichment, or an investigation
run. Validate those separately in the target tenant.

Use the data to show evidence correlation and analyst review. Do not claim that
Wise executed a response, that a synthetic record is native vendor telemetry,
or that an imported raw event automatically starts a Wise investigation.
