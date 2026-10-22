# Services Narnia — synthetic security telemetry

This repository hosts fictional training data for a Trellix Wise / Splunk IT-to-OT investigation demonstration.

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
