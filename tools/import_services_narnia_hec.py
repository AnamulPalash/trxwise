#!/usr/bin/env python3
"""Import Services Narnia NDJSON into Splunk HEC with per-event metadata.

All source events are synthetic. This tool sends telemetry to a Splunk lab,
not to Trellix Wise directly. Python 3.9+, standard library only.

Dry run (needs no token):
 python3 tools/import_services_narnia_hec.py data/services_narnia_wise_rich_4000.json --dry-run

Live import (HEC token must be authorised for the selected index):
 export SPLUNK_HEC_TOKEN="YOUR_SPLUNK_HEC_TOKEN"
 python3 tools/import_services_narnia_hec.py data/services_narnia_wise_rich_4000.json \
  --url https://SPLUNK_HOST:8088/services/collector/event --index services_narnia_wise
"""
import argparse
import collections
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request


def to_epoch(timestamp):
    # UTC timestamps from the published file, e.g. 2026-10-22T05:53:00Z
    return dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp()


def read_events(filename):
    with open(filename, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if line.strip():
                try:
                    obj = json.loads(line)
                    if not isinstance(obj, dict):
                        raise ValueError("event must be a JSON object")
                    for field in ("timestamp", "event_id", "sourcetype", "scenario"):
                        if not obj.get(field):
                            raise ValueError(f"missing {field}")
                    to_epoch(obj["timestamp"])
                    yield obj
                except (ValueError, json.JSONDecodeError) as exc:
                    raise RuntimeError(f"Invalid event on line {lineno}: {exc}") from exc


def payload(event, index):
    event_host = (
        event.get("dest") if isinstance(event.get("dest"), str)
        and event.get("dest").upper().startswith("NARNIA-")
        else event.get("src_host")
        or event.get("workstation")
        or "services-narnia-simulator"
    )
    return {
        "time": to_epoch(event["timestamp"]),
        "host": event_host,
        "index": index,
        "source": "services_narnia_synthetic_lab",
        "sourcetype": event["sourcetype"],
        "event": event,
    }


def send_batch(url, token, batch):
    data = ("\n".join(json.dumps(x, separators=(",", ":")) for x in batch) + "\n").encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Splunk {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as response:
        body = response.read().decode("utf-8")
        try:
            res = json.loads(body)
        except ValueError as exc:
            raise RuntimeError(f"Unexpected HEC response: {body[:300]}") from exc
        if res.get("code") != 0:
            raise RuntimeError(f"Splunk HEC refused batch: {res}")


def main():
    parser = argparse.ArgumentParser(description="Import synthetic Services Narnia JSON via Splunk HEC")
    parser.add_argument("file", help="newline-delimited JSON dataset")
    parser.add_argument("--url", default="", help="full HTTPS URL to /services/collector/event")
    parser.add_argument("--index", default="services_narnia_wise")
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not (1 <= args.batch_size <= 500):
        parser.error("--batch-size must be between 1 and 500")
    if not args.dry_run and (not args.url.startswith("https://") or not args.url.endswith("/services/collector/event")):
        parser.error("Use an HTTPS Splunk HEC endpoint ending in /services/collector/event")
    token = os.environ.get("SPLUNK_HEC_TOKEN", "")
    if not args.dry_run and not token:
        parser.error("Set SPLUNK_HEC_TOKEN in the environment")
    counters = collections.Counter()
    cases = 0
    batches = []
    total = 0
    try:
        for obj in read_events(args.file):
            counters[obj["sourcetype"]] += 1
            cases += bool(obj.get("attack_event") is True)
            total += 1
            batches.append(payload(obj, args.index))
            if len(batches) >= args.batch_size:
                if not args.dry_run:
                    send_batch(args.url, token, batches)
                batches.clear()
        if batches and not args.dry_run:
            send_batch(args.url, token, batches)
    except urllib.error.URLError as exc:
        sys.exit(f"Splunk connection failed: {exc}. Check DNS, TLS trust, port, token and HEC configuration.")
    except Exception as exc:
        sys.exit(f"Import validation failed: {exc}")
    print(f"{'Validated' if args.dry_run else 'Submitted'}: {total} events; linked attack events: {cases}")
    for source, number in sorted(counters.items()):
        print(f"  {source:26} {number}")
    if not args.dry_run:
        print("HEC accepted the events. Run Splunk searches to confirm indexing and fields.")


if __name__ == "__main__":
    main()
