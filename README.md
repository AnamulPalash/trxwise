# Services Narnia — synthetic security telemetry

## New: Detailed Services Narnia → Splunk → Wise lab

**Recommended dataset:** [services_narnia_wise_rich_4000.json](https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_wise_rich_4000.json) — 4,000 security-rich NDJSON events (37 linked attack events), ten simulated product sources, with process trees, C2 sessions, IAM activity, DLP and OT register events.

### One command: download + refresh timestamps (no HEC token needed)

Run this **single command** in the terminal on your Mac, Linux PC or lab VM (requires Python 3 and `curl`):

```bash
curl -fsSL -o services_narnia_wise_rich_4000.json https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_wise_rich_4000.json && curl -fsSL -o rebase_services_narnia_timestamps.py https://raw.githubusercontent.com/AnamulPalash/trxwise/main/tools/rebase_services_narnia_timestamps.py && python3 rebase_services_narnia_timestamps.py services_narnia_wise_rich_4000.json -o services_narnia_wise_latest.json --latest-minutes-ago 0
```

It downloads the 4,000-event dataset and Python refresh script, then creates **`services_narnia_wise_latest.json` in the current folder**, setting the newest event timestamp to current UTC time. The original file is left unchanged. Upload the generated `services_narnia_wise_latest.json` through **Splunk → Settings → Add Data → Upload**; select a dedicated Events index (`services_narnia_wise`) and configure the timestamp field `timestamp` with UTC format `%Y-%m-%dT%H:%M:%SZ` if the preview does not parse it. Set search time picker to **All time** to verify 4,000 records. A Web upload gives all events one real Splunk metadata sourcetype; per-product sourcetypes need HEC or other configuration.

**[Full lab import + Wise investigation guide](docs/services_narnia_wise_rich_demo.md)** · [HEC importer](tools/import_services_narnia_hec.py) · [Timestamp refresh](tools/rebase_services_narnia_timestamps.py)

Use Splunk Web upload for a quick start; use the provided HEC importer if you want each source record to receive its original Splunk metadata sourcetype. Wise still requires a compatible configured Ingest and/or Enrich integration, and source alerts eligible for investigations. All content is synthetic. Do not commit tokens or real customer telemetry to this public repository.

---


This repository hosts fictional training data for a Trellix Wise / Splunk IT-to-OT investigation demonstration.

## Extended 10,000-event demo dataset

- **[Download the 10,000-event file](https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_10000_events.json)** (NDJSON, 10,000 events, about 2 MB)
- Runs from **2026-10-15 03:35 UTC** through **2026-10-22 03:35 UTC**, including the 12-event phishing-to-OT attack around **2026-10-22 03:15–03:21 UTC**.
- Sourcetype proportions: Trellix ENS 1,000; EDR 1,000; NX 2,000; Palo Alto 1,500; Okta 750; Windows Security 750; Trellix Email 1,000; DLP 500; IPS 500; and Modbus 1,000.
- File has one JSON object per line and uses ISO UTC `timestamp` (not Splunk's reserved `_time`).
- Recommended: create **a new index `services_narnia_10k`** and reuse the `services_narnia_json` sourcetype **only if** its timestamp extraction preview is correct. The `sourcetype` inside each JSON event is a data field; a single Web upload still assigns one metadata sourcetype to the whole file.
- Set Splunk search time picker to **All time** initially. The US time zone may display the attack as **21 October 2026** rather than 22 October.

Download on a lab VM:

```bash
curl -fL -o services_narnia_10000_events.json https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_10000_events.json
```

Validation query after import:

```spl
index=services_narnia_10k earliest=0
| stats count as events min(_time) as earliest max(_time) as latest
| convert ctime(earliest) ctime(latest)
```

Expected event count: **10,000**. The dataset contains synthetic benign and alert activity; none is from actual endpoints or PLCs.

## Direct downloads for lab VMs

- **[Splunk import: newline-delimited JSON](https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_security_events.json)**
- [JSON array for tools expecting one array](https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_security_events_array.json)
- [Splunk HTTP Event Collector: newline-delimited HEC messages](https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_hec_events.ndjson)

On the lab VM:

```bash
curl -fL -o services_narnia_security_events.json https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_security_events.json
```

The import file has **12 synthetic events, one JSON object per line**, representing 10 telemetry source types. Each event has a standard ISO 8601 UTC `timestamp` (e.g. `2026-10-21T05:06:33Z`). The file deliberately does **not** have a JSON `_time` key because Splunk reserves `_time` for its internal numeric epoch timestamp. This corrects the earlier version that rendered `NaN/NaN/NaN` in Splunk Web.

## Upload into Splunk Web

1. Open **Settings → Add Data → Upload**, and choose `services_narnia_security_events.json`.
2. On **Set Source Type**, select JSON / `_json`, confirm each line becomes one event, and inspect the timestamp preview.
3. If the timestamp preview is incorrect, open **Timestamp → Advanced** and set:
   - **Timestamp fields:** `timestamp`
   - **Timestamp format:** `%Y-%m-%dT%H:%M:%SZ`
   - **Time zone:** UTC
4. Select or create index `services_narnia`. For a clean test without duplicate old events, optionally create a new index `services_narnia_fixed` and use that in searches.
5. Set the search time picker to **All time**; these test timestamps are fixed in October 2026.

Verify:

```spl
index=services_narnia earliest=0
| eval parsed_utc=strftime(_time,"%Y-%m-%dT%H:%M:%SZ")
| table _time parsed_utc timestamp vendor product action
```

If you imported into `services_narnia_fixed`, change the index name in the query.

**Timezone note:** `Z` means UTC; a US timezone can display the same event on the preceding calendar day. That does **not** cause `NaN`. Splunk converts indexed epoch time for display according to your user timezone.

Uploading one file with sourcetype `_json` means all 12 events share the same **Splunk metadata** sourcetype. Their `sourcetype` JSON fields record the simulated source type but do not create different metadata sourcetypes. For distinct metadata sourcetypes, use the HEC payload version: its outer `time` field contains numeric epoch seconds and outer `sourcetype` field defines the true Splunk sourcetype.

## Optional Docker static file host

```bash
git clone https://github.com/AnamulPalash/trxwise.git
cd trxwise
docker compose up -d
# http://YOUR_DOCKER_HOST:8080/services_narnia_security_events.json
```

Docker must be deployed on your host; a GitHub commit does not launch the container. Expose the HTTP port only in your trusted lab network or through appropriate access controls.

No live PLC or security infrastructure was contacted. The Modbus event is fabricated telemetry, not proof of actual operational impact.
