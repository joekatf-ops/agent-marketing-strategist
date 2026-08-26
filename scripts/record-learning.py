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
    "learning",
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
HARD_RULE_CLASSIFICATIONS = {
    "factual_correction",
    "compliance_correction",
    "voice_rule",
}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EVENT_ID = re.compile(r"^LEARN-[A-Z0-9]+$")


def validate_event(event: dict) -> list[str]:
    if not isinstance(event, dict):
        return ["event must be a JSON object"]
    errors = [f"missing required field: {field}" for field in REQUIRED if field not in event]
    if errors:
        return errors
    event_id = event.get("event_id")
    if event_id is not None and (
        not isinstance(event_id, str) or not EVENT_ID.fullmatch(event_id)
    ):
        errors.append("event_id must match LEARN-[A-Z0-9]+")
    brand_slug = event["brand_slug"]
    if not isinstance(brand_slug, str) or not SLUG.fullmatch(brand_slug):
        errors.append("brand_slug must be lowercase hyphenated text")
    market = event["market"]
    if not isinstance(market, str) or len(market) < 2:
        errors.append("market must contain at least 2 characters")
    for field in ("product_id", "source_asset_id", "reason", "learning", "author"):
        value = event[field]
        if not isinstance(value, str) or not value:
            errors.append(f"{field} must not be empty")
    for field in ("before", "after"):
        if not isinstance(event[field], str):
            errors.append(f"{field} must be a string")
    memory_key = event.get("memory_key")
    if memory_key is not None and (
        not isinstance(memory_key, str) or not memory_key.strip()
    ):
        errors.append("memory_key must be a non-empty string")
    supersedes = event.get("supersedes")
    if supersedes is not None and (
        not isinstance(supersedes, str) or not EVENT_ID.fullmatch(supersedes)
    ):
        errors.append("supersedes must match LEARN-[A-Z0-9]+")
    if (
        event["status"] == "approved"
        and isinstance(event["classification"], str)
        and event["classification"] in HARD_RULE_CLASSIFICATIONS | {"preference"}
        and (not isinstance(memory_key, str) or not memory_key.strip())
    ):
        errors.append("approved hard rules and preferences require memory_key")
    if (
        not isinstance(event["classification"], str)
        or event["classification"] not in CLASSIFICATIONS
    ):
        errors.append(f"invalid classification: {event['classification']}")
    if not isinstance(event["status"], str) or event["status"] not in STATUSES:
        errors.append(f"invalid status: {event['status']}")
    if not isinstance(event["scope"], str) or event["scope"] not in SCOPES:
        errors.append(f"invalid scope: {event['scope']}")
    confidence = event["confidence"]
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        errors.append("confidence must be a number from 0 to 1")
    elif not 0 <= confidence <= 1:
        errors.append("confidence must be a number from 0 to 1")
    if isinstance(event["before"], str) and event["before"] == event["after"]:
        errors.append("before and after must differ")
    try:
        timestamp = event["timestamp"]
        parsed = dt.datetime.fromisoformat(timestamp)
        if "T" not in timestamp or parsed.tzinfo is None:
            raise ValueError
    except (AttributeError, TypeError, ValueError):
        errors.append("timestamp must be an ISO 8601 date-time")
    return errors


def manifest_slug(folder: pathlib.Path) -> str:
    manifest = folder / "brand.yml"
    if not manifest.is_file():
        raise FileNotFoundError(f"brand manifest not found: {manifest}")
    match = re.search(r'^\s*slug:\s*["\']?([^"\'\s]+)', manifest.read_text(), re.MULTILINE)
    if not match:
        raise ValueError("brand.yml does not contain brand.slug")
    return match.group(1)


def configured_rule_approvers(folder: pathlib.Path) -> set[str]:
    text = (pathlib.Path(folder) / "brand.yml").read_text()
    inline = re.search(r"(?m)^\s*rule_approvers:\s*\[([^]]*)\]", text)
    if inline:
        body = inline.group(1).strip()
        if not body:
            return set()
        return {
            item.strip().strip('"\'')
            for item in body.split(",")
            if item.strip().strip('"\'')
        }
    block = re.search(r"(?m)^\s*rule_approvers:\s*$", text)
    if not block:
        return set()
    approvers = set()
    for line in text[block.end() :].splitlines():
        match = re.match(r"^\s+-\s*(.+?)\s*$", line)
        if not match:
            if line.strip():
                break
            continue
        value = match.group(1).strip().strip('"\'')
        if value:
            approvers.add(value)
    return approvers


def load_events(folder: pathlib.Path) -> list[dict]:
    folder = pathlib.Path(folder)
    connected_slug = manifest_slug(folder)
    ledger = folder / "learning" / "learning-events.jsonl"
    if not ledger.is_file():
        return []
    events = []
    for line_number, line in enumerate(ledger.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"invalid JSON in learning ledger at line {line_number}"
            ) from error
        errors = validate_event(event)
        if errors:
            raise ValueError(
                f"invalid learning event at line {line_number}: {'; '.join(errors)}"
            )
        if event["brand_slug"] != connected_slug:
            raise ValueError(
                f"event brand {event['brand_slug']} does not match connected brand "
                f"{connected_slug} at line {line_number}"
            )
        events.append(event)
    return events


def memory_record(event: dict) -> dict:
    record = {
        "event_id": event["event_id"],
        "classification": event["classification"],
        "scope": event["scope"],
        "market": event["market"],
        "product_id": event["product_id"],
        "source_asset_id": event["source_asset_id"],
        "value": event["learning"],
        "reason": event["reason"],
        "confidence": event["confidence"],
        "approved_by": event["author"],
        "approved_at": event["timestamp"],
    }
    if event.get("memory_key"):
        record["memory_key"] = event["memory_key"]
    if event.get("supersedes"):
        record["supersedes"] = event["supersedes"]
    return record


def rebuild_active_memory(folder: pathlib.Path) -> pathlib.Path:
    folder = pathlib.Path(folder)
    connected_slug = manifest_slug(folder)
    events = load_events(folder)
    approved = [event for event in events if event["status"] == "approved"]
    superseded = {event["supersedes"] for event in approved if event.get("supersedes")}

    active_rules = []
    approved_insights = []
    preference_signals = []
    scoped_notes = []
    universal_candidates = []
    for event in approved:
        if event["event_id"] in superseded or event["classification"] == "accidental_edit":
            continue
        record = memory_record(event)
        if event["scope"] == "universal_candidate":
            universal_candidates.append(record)
        elif event["classification"] in HARD_RULE_CLASSIFICATIONS:
            rule = dict(record)
            rule["rule"] = rule.pop("value")
            active_rules.append(rule)
        elif event["classification"] == "strategic_learning":
            approved_insights.append(record)
        elif event["classification"] == "preference":
            preference_signals.append(record)
        elif event["classification"] in {"execution_specific", "editor_preference"}:
            scoped_notes.append(record)

    grouped_preferences: dict[tuple[str, str, str, str], list[dict]] = {}
    for record in preference_signals:
        normalized = " ".join(record["value"].lower().split())
        key = (
            record["scope"],
            record["market"],
            record["product_id"],
            f"{record['memory_key']}:{normalized}",
        )
        grouped_preferences.setdefault(key, []).append(record)
    preference_candidates = []
    for (scope, market, product_id, _), records in sorted(grouped_preferences.items()):
        distinct_assets = {record["source_asset_id"] for record in records}
        if len(distinct_assets) < 3:
            continue
        preference_candidates.append(
            {
                "candidate": records[0]["value"],
                "scope": scope,
                "market": market,
                "product_id": product_id,
                "signal_count": len(distinct_assets),
                "source_event_ids": [record["event_id"] for record in records],
                "status": "proposed",
            }
        )

    keyed_rules: dict[str, list[dict]] = {}
    for rule in active_rules:
        if rule.get("memory_key"):
            keyed_rules.setdefault(rule["memory_key"], []).append(rule)
    unresolved_conflicts = []
    for memory_key, rules in sorted(keyed_rules.items()):
        if len({rule["rule"] for rule in rules}) > 1:
            unresolved_conflicts.append(
                {
                    "memory_key": memory_key,
                    "event_ids": [rule["event_id"] for rule in rules],
                    "values": [rule["rule"] for rule in rules],
                }
            )

    memory = {
        "schema_version": 1,
        "brand_slug": connected_slug,
        "learning_version": len(events),
        "source_event_count": len(events),
        "last_event_id": events[-1]["event_id"] if events else None,
        "active_rules": active_rules,
        "approved_insights": approved_insights,
        "preference_signals": preference_signals,
        "preference_candidates": preference_candidates,
        "scoped_notes": scoped_notes,
        "universal_candidates": universal_candidates,
        "unresolved_conflicts": unresolved_conflicts,
    }
    destination = folder / "learning" / "active-memory.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(memory, indent=2, sort_keys=True) + "\n")
    temporary.replace(destination)
    return destination


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
    if event["status"] == "approved" and event["classification"] != "accidental_edit":
        approvers = configured_rule_approvers(folder)
        if not approvers:
            raise ValueError("no rule approvers configured in brand.yml")
        if event["author"] not in approvers:
            raise ValueError(
                f"author is not an approved rule approver: {event['author']}"
            )

    stored = dict(event)
    event_id = stored.get("event_id") or f"LEARN-{uuid.uuid4().hex[:12].upper()}"
    stored["event_id"] = event_id
    ledger = folder / "learning" / "learning-events.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    existing_events = load_events(folder)
    if any(existing.get("event_id") == event_id for existing in existing_events):
        raise ValueError(f"event_id already exists: {event_id}")
    if stored.get("supersedes") and not any(
        existing.get("event_id") == stored["supersedes"] for existing in existing_events
    ):
        raise ValueError(f"supersedes event does not exist: {stored['supersedes']}")
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(stored, ensure_ascii=False, sort_keys=True) + "\n")
    rebuild_active_memory(folder)
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
