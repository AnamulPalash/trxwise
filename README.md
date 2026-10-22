# Services Narnia — synthetic security telemetry

This repository hosts **synthetic training data only** for a Trellix Wise / Splunk IT-to-OT investigation demonstration.

## Direct downloads for lab VMs

- [Splunk import (NDJSON, .json extension)](https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_security_events.json)
- [JSON array for other import tools](https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_security_events_array.json)
- [Splunk HEC payloads (NDJSON)](https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_hec_events.ndjson)

On a lab VM with `curl`:

```bash
curl -fL -o services_narnia_security_events.json https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/services_narnia_security_events.json
```

In Splunk Web, use **Settings → Add Data → Upload**, pick the downloaded `.json`, set sourcetype to `_json`, and select/create index `services_narnia`. Set **time range: All time** when searching the fixed historical timestamps. The file contains 12 lines/events covering 10 sourcetypes, but when uploaded via the Splunk UI as one file, the per-event `sourcetype` JSON key does **not** change Splunk metadata. For individual source types, use HEC events instead.

## Optional Docker static-file server

```bash
docker compose up -d --build
# http://YOUR_DOCKER_HOST:8080/services_narnia_security_events.json
```

The Docker setup serves the contents of `data/` as static downloads through Nginx. Docker deployment must be performed on the host; pushing to GitHub alone does not deploy a running container. Publish the port only in a trusted lab environment or secure it using existing access controls.

**All events are fictional.** The Modbus event is synthetic telemetry and no PLC was contacted. Do not use as an actual threat-indicator feed.
