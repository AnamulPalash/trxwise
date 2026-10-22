# Services Narnia — detailed Splunk-to-Trellix Wise lab demo

**Scope:** Public repository contains fictional training events and non-secret importer scripts ONLY. No internal Trellix architecture, runbooks or credentials are included.

## Download the new detailed file

**[services_narnia_wise_rich_4000.json](https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_wise_rich_4000.json)**

It is NDJSON (one JSON event per line; `.json` extension), not a single JSON array.

- **4,000 total events**, 10 product/source categories, 37 events in a single correlated fictional attack (case `SN-OT-2026-1022`).
- Background events span **15–22 October 2026 (UTC)**. The coordinated attack occurs on **22 October 2026 at 05:53–06:03 UTC**. Your US lab timezone may display **21 October**.
- Expanded fields include actor, process parents/PIDs, command-line placeholders, attachment/message IDs, signatures, identities/sessions, TLS sessions/JA3, firewall zones, DLP classifications, jump-host access and Modbus function/register details.
- Commands marked `[INERT_...]` are placeholder strings; the data does not contain runnable payloads. The control-system events do not establish physical effects.
- All telemetry is synthetic and **modelled on categories**, not actual exported schemas guaranteed to match production Trellix, PAN-OS, Okta or PLC logs.
- A few indicator strings reflect the fictional storyline but are not verified malicious infrastructure; never upload as real block-list intelligence.

### File distribution

| JSON `sourcetype` field | Events |
|---|---:|
| `trellix:etp` | 400 |
| `trellix:ens:exploit` | 400 |
| `trellix:edr:event` | 400 |
| `trellix:nx` | 800 |
| `pan:threat` | 600 |
| `Okta:Security` | 300 |
| `WinEventLog:Security` | 300 |
| `trellix:dlp:incident` | 200 |
| `trellix:ips` | 200 |
| `scada:modbus` | 400 |
| **Total** | **4,000** |

### One command: download + refresh timestamps (no HEC token needed)

Run this **single command** in the terminal on your Mac, Linux PC or lab VM (requires Python 3 and `curl`):

```bash
curl -fsSL -o services_narnia_wise_rich_4000.json https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_wise_rich_4000.json && curl -fsSL -o rebase_services_narnia_timestamps.py https://raw.githubusercontent.com/AnamulPalash/trxwise/main/tools/rebase_services_narnia_timestamps.py && python3 rebase_services_narnia_timestamps.py services_narnia_wise_rich_4000.json -o services_narnia_wise_latest.json --latest-minutes-ago 0
```

It downloads the 4,000-event dataset and Python refresh script, then creates **`services_narnia_wise_latest.json` in the current folder**, setting the newest event timestamp to current UTC time. The original file is left unchanged. Upload the generated `services_narnia_wise_latest.json` through **Splunk → Settings → Add Data → Upload**; select a dedicated Events index (`services_narnia_wise`) and configure the timestamp field `timestamp` with UTC format `%Y-%m-%dT%H:%M:%SZ` if the preview does not parse it. Set search time picker to **All time** to verify 4,000 records. A Web upload gives all events one real Splunk metadata sourcetype; per-product sourcetypes need HEC or other configuration.

## Option A — Import in Splunk Web (simplest)

1. From the VM download the file:

   ```bash
   curl -fL -o services_narnia_wise_rich_4000.json https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_wise_rich_4000.json
   ```

2. In **Splunk → Settings → Add Data → Upload**, choose the file.
3. Use built-in **`_json`** or a new custom JSON sourcetype, e.g. `services_narnia_json`. Make sure the preview shows **one record per JSON line** and extracts the `timestamp` field.
4. If the preview timestamp is wrong, configure timestamp field `timestamp`, format `%Y-%m-%dT%H:%M:%SZ`, timezone **UTC**. Do not use JSON `_time` strings; Splunk reserves `_time` internally.
5. In **Input Settings**, select/create index `services_narnia_wise` with type **Events**.
6. Review, submit, and set time picker **All time** initially.

**Limitation:** All 4,000 records receive the *same real Splunk metadata sourcetype* on a single Web file upload. Their internal JSON `sourcetype` values do NOT change metadata per event. Source-specific CIM correlation and data-model acceleration need additional configuration. For actual per-product metadata, use Option B.

## Option B — HEC, preserving ten Splunk sourcetypes (preferred for technical demo)

The repository includes `tools/import_services_narnia_hec.py`. It constructs one HEC envelope per JSON event, using the original event-specific `sourcetype`, epoch `time`, `host`, and selected `index`. Splunk documents this envelope format here:

https://help.splunk.com/en/splunk-enterprise/get-started/get-data-in/10.6/get-data-with-http-event-collector/format-events-for-http-event-collector

Prerequisites: HEC enabled on your Splunk lab, authorised token restricted to the lab index, connectivity to **HTTPS/8088**, and trusted TLS certificate. Do **not** disable certificate verification to make the demo work.

```bash
curl -fL -o services_narnia_wise_rich_4000.json https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_wise_rich_4000.json
curl -fL -o import_services_narnia_hec.py https://raw.githubusercontent.com/AnamulPalash/trxwise/main/tools/import_services_narnia_hec.py

# Validate all events without sending:
python3 import_services_narnia_hec.py services_narnia_wise_rich_4000.json --dry-run

# Once Splunk HEC is configured:
export SPLUNK_HEC_TOKEN='YOUR_LAB_HEC_TOKEN'
python3 import_services_narnia_hec.py services_narnia_wise_rich_4000.json \
  --url https://YOUR_SPLUNK_HOST:8088/services/collector/event \
  --index services_narnia_wise
unset SPLUNK_HEC_TOKEN
```

Avoid importing the SAME file via BOTH options into the SAME index: that creates duplicates.

### Refresh timestamps for a newer Wise polling window

The published dataset has static October 2026 timestamps. If you're importing on a later day, Wise might have a short Ingest lookback window and will never pick up the old alerts. Download the companion [timestamp rebase script](https://raw.githubusercontent.com/AnamulPalash/trxwise/main/tools/rebase_services_narnia_timestamps.py), then run:

```bash
python3 rebase_services_narnia_timestamps.py services_narnia_wise_rich_4000.json -o services_narnia_wise_latest.json --latest-minutes-ago 5
```

This preserves the chronology and shifts the most recent event to five minutes ago. Import `services_narnia_wise_latest.json` into a **new/empty lab index** to avoid duplicates.

## Splunk validation searches

**1. Raw count (expected 4,000):**

```spl
index=services_narnia_wise earliest=0
| stats count AS total
```

**2. Attack timeline (expected 37 rows):**

```spl
index=services_narnia_wise earliest=0 case_id="SN-OT-2026-1022"
| spath input=_raw path=sourcetype output=event_source
| sort 0 _time
| table _time event_id event_source stage severity user src_ip dest_ip signature action
```

**3. Source categories (ten if per-event extraction works; HEC metadata should show ten):**

```spl
index=services_narnia_wise earliest=0
| spath input=_raw path=sourcetype output=original_event_source
| stats count BY original_event_source
| sort -count
```

**4. Phishing blast radius:**

```spl
index=services_narnia_wise earliest=0 campaign_id="SN-PHISH-1022"
| stats values(action) AS mail_disposition values(message_id) AS message_ids BY recipient
```

**5. Cross-product IT-to-OT findings:**

```spl
index=services_narnia_wise earliest=0 case_id="SN-OT-2026-1022"
| spath input=_raw path=sourcetype output=event_source
| stats count AS evidence_events values(stage) AS stages values(signature) AS detections dc(event_source) AS source_families BY case_id
```

**6. Alert candidates for ingestion/search:**

```spl
index=services_narnia_wise earliest=0 case_id="SN-OT-2026-1022"
| search severity IN ("high","critical")
| table _time event_id sourcetype stage signature user src_ip dest_ip
| sort 0 _time
```

These searches use ordinary search-time field extraction. Don't use `tstats summariesonly=true` until actual Splunk CIM data models are installed, populated and correctly mapped; the JSON alone does not define CIM data models.

## Connect to Trellix Wise

Your supplied internal Wise documentation describes three different integration feature roles:

- **Ingest**: pull/receive eligible external security alerts that may start investigation runs.
- **Enrich**: expose external search/tool capability during a run; allows further Splunk evidence lookups if the installed connector has that feature.
- **Egest**: send outputs/results to external systems. Configuring Splunk **Egest** does not make Wise read your Splunk lab.

In your Wise tenant:

1. As Admin/Super Admin open **Integrations → Add Integration**.
2. Find Splunk in the current catalogue. Name it `Splunk — Services Narnia Lab`.
3. Configure connection, allowed index/search scope, appropriate **read-only search credentials**, and enable **Ingest and/or Enrich** if those features appear for your installed connector. These features are disabled by default when an instance is created. The integration may require feature-specific credentials.
4. **Verify/Test connectivity**, then separately validate successful polling/search and an actual investigation trigger. The integration's Enabled status reflects its **last connectivity test**, not continuous health and not confirmation of index-specific ingestion.
5. Open **Investigations** (default Last 7 Days) and inspect a produced run. In **Evidence**, look for linked indicators and supporting SPL queries. In **Thought Process**, inspect the tools used and their results. If no run was generated, verify ingestion configuration/alert eligibility, lookback and agent permissions. A random raw indexed event won't automatically create an investigation.
6. Keep response actions disabled or analyst-approved in the synthetic demo. The supplied Response Actions file is a proposal, not proof of specific live integrations.

### Demo starter investigation request

> Investigate the fictional Services Narnia case SN-OT-2026-1022 using the connected Splunk index services_narnia_wise. Correlate phishing mail from contractor-support@darknarnia-vault.xyz, Excel-launched PowerShell on NARNIA-ENG-04 (10.10.20.44), outbound connections to 185.220.101.42:8443, Okta session replay, RDP to NARNIA-JUMP-01, DLP blocks, IPS IT-to-OT boundary events and Modbus traffic to 192.168.100.110:502. Create a UTC timeline, list evidence and source events, identify affected assets and MITRE mappings, separate observed facts from hypotheses, and recommend human-approved responses only.

A free-text Wise prompt is useful only if your installed UI provides a connected hunting/investigation workflow that accepts it. Otherwise initiate the run through its supported Ingest/alert path.

## Troubleshooting checklist

| Symptom | Check |
|---|---|
| Splunk Time displays NaN | Remove string `_time` key and parse ISO `timestamp` in UTC |
| 4,000 records but one Splunk sourcetype | Expected for Option A; use HEC for per-event metadata |
| Missing attack events | `case_id="SN-OT-2026-1022"` and time picker All time |
| Wise integration tests successfully, no cases | Ingest enabled? Alert eligibility? Poll checkpoint/lookback? Tenant/agent permissions? |
| Wise report has no Splunk evidence | Enrich enabled? Read-only search authorised for this index? Agent tools and query results in Thought Process? |
| Old data not polled | Rebase timestamps and ingest into a clean index, or configure supported lookback window |
| HEC TLS error | Install the lab CA chain/trust rather than suppress verification |

**Status:** Dataset structurally verified at generation and GitHub file commit confirmed; live Splunk HEC and Wise investigation execution have not yet been tested in your lab. No vendor-native field guarantee or CIM acceleration claim is made.
