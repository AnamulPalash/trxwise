#!/usr/bin/env python3
"""Move a synthetic Services Narnia NDJSON dataset to the present.

Preserves relative timeline gaps and all security fields. Does not contact
Splunk, Wise, or any service. Use before an ingest workflow restricted to
recent alerts. Output goes to a NEW file.
"""
import argparse
import datetime as dt
import json
from pathlib import Path


def parse(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("-o", "--output", default="services_narnia_wise_latest.json")
    p.add_argument("--latest-minutes-ago", type=int, default=5)
    args = p.parse_args()
    if args.latest_minutes_ago < 0:
        p.error("--latest-minutes-ago must not be negative")
    infile, outfile = Path(args.input), Path(args.output)
    if infile.resolve() == outfile.resolve():
        p.error("Output must not overwrite input")
    events = [json.loads(line) for line in infile.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not events:
        p.error("Input is empty")
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    target = now - dt.timedelta(minutes=args.latest_minutes_ago)
    newest = max(parse(e["timestamp"]) for e in events)
    delta = target - newest
    for e in events:
        e["timestamp"] = (parse(e["timestamp"]) + delta).strftime("%Y-%m-%dT%H:%M:%SZ")
    events.sort(key=lambda e: (e["timestamp"], e.get("event_id", "")))
    with outfile.open("w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, separators=(",", ":")) + "\n")
    print(f"Wrote {len(events)} events to {outfile}; newest event {events[-1]['timestamp']}.")


if __name__ == "__main__":
    main()
