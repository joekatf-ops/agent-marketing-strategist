#!/usr/bin/env python3
"""Validate and append one human-revision learning event."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import uuid


REQUIRED = (
    "brand_slug",
    "market",
    "product_id",
    "source_asset_id",
    "before",
    "after",
    "reason",
    "scope",
    "classification",
    "status",
    "confidence",
    "author",
    "timestamp",
)
CLASSIFICATIONS = {
    "factual_correction",
    "compliance_correction",
    "voice_rule",
    "preference",
    "execution_specific",
    "strategic_learning",
    "editor_preference",
    "accidental_edit",
}
STATUSES = {"proposed", "approved", "rejected", "experimental"}
SCOPES = {"execution", "product", "market", "brand", "editor", "universal_candidate"}


def validate_event(event: dict) -> list[str]:
    errors = [f"missing required field: {field}" for field in REQUIRED if field not in event]
    if errors:
        return errors
    if event["classification"] not in CLASSIFICATIONS:
        errors.append(f"invalid classification: {event['classification']}")
    if event["status"] not in STATUSES:
        errors.append(f"invalid status: {event['status']}")
    if event["scope"] not in SCOPES:
        errors.append(f"invalid scope: {event['scope']}")
    confidence = event["confidence"]
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        errors.append("confidence must be a number from 0 to 1")
    elif not 0 <= confidence <= 1:
        errors.append("confidence must be a number from 0 to 1")
    if event["before"] == event["after"]:
        errors.append("before and after must differ")
    try:
        dt.datetime.fromisoformat(event["timestamp"])
    except (TypeError, ValueError):
        errors.append("timestamp must be ISO 8601")
    return errors


def manifest_slug(folder: pathlib.Path) -> str:
    manifest = folder / "brand.yml"
    if not manifest.is_file():
        raise FileNotFoundError(f"brand manifest not found: {manifest}")
    match = re.search(r'^\s*slug:\s*["\']?([^"\'\s]+)', manifest.read_text(), re.MULTILINE)
    if not match:
        raise ValueError("brand.yml does not contain brand.slug")
    return match.group(1)


def append_event(folder: pathlib.Path, event: dict) -> str:
    folder = pathlib.Path(folder)
    errors = validate_event(event)
    if errors:
        raise ValueError("; ".join(errors))
    connected_slug = manifest_slug(folder)
    if event["brand_slug"] != connected_slug:
        raise ValueError(
            f"event brand {event['brand_slug']} does not match connected brand {connected_slug}"
        )

    stored = dict(event)
    event_id = stored.get("event_id") or f"LEARN-{uuid.uuid4().hex[:12].upper()}"
    stored["event_id"] = event_id
    ledger = folder / "learning" / "learning-events.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(stored, ensure_ascii=False, sort_keys=True) + "\n")
    return event_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brand_folder", type=pathlib.Path)
    parser.add_argument("event_json", type=pathlib.Path)
    args = parser.parse_args()
    event = json.loads(args.event_json.read_text())
    event_id = append_event(args.brand_folder, event)
    print(f"Recorded learning event: {event_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
