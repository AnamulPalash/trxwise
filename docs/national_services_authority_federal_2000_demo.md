# National Services Authority: Federal SOC training dataset

This repository contains a **fictional, synthetic** 2,000-event dataset for a
Trellix Wise and Splunk lab. It models a federal-department SOC investigation,
not an actual government department or vendor export.

## Scenario

Case `FDC-SOC-2026-1027` follows a phishing email to a user workstation,
inert PowerShell telemetry, synthetic process-injection indicators, C2-like
network records, session-reuse evidence, lateral movement to a privileged jump
host, blocked data transfer, and denied access to a protected citizen-services
application. The final analyst decision is evidence-led and human approved.

- 2,000 NDJSON records, one object per line
- 20 linked attack events across ten source categories
- Every record includes `synthetic: true` and
  `simulation_origin: synthetic_training_telemetry`
- No payloads, live credentials, real IPs, real government data, or external
  network actions are included

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

Expected: `total=2000`, `source_categories=10`, `synthetic_flags=true`.

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

## Wise lab boundary

Configure the installed Splunk connector only with its supported Ingest and/or
Enrich features and read-only credentials. A successful connection test does
not prove index polling, alert eligibility, enrichment, or an investigation
run. Validate those separately in the target tenant.

Use the data to show evidence correlation and analyst review. Do not claim that
Wise executed a response, that a synthetic record is native vendor telemetry,
or that an imported raw event automatically starts a Wise investigation.
