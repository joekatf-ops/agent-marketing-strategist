#!/usr/bin/env python3
"""Sync the swipe corpus from a Foreplay board.

Fetches a board, maps each ad to the swipe-entry shape, and merges into
`corpus/swipe/entries.json` without discarding human work: an existing entry keeps
its annotation and its `reviewed` flag, and only the fetched fields are refreshed.

    FOREPLAY_API_KEY=... python3 scripts/sync-swipe-corpus.py --board-id <id> --board-name best_ads

Standard library only, so it runs in CI without installing anything.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://public.api.foreplay.co"
BOARD_ADS = "/api/board/ads"
BOARD_BRANDS = "/api/board/brands"
PAGE_LIMIT = 250
TIMEOUT_SECONDS = 60

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "corpus" / "swipe" / "entries.json"

FORMATS = {"video", "image", "dco", "carousel", "text"}


def request(path: str, key: str, params: dict[str, object]) -> dict:
    """GET one page. Tries bearer auth first, then the raw key.

    The OpenAPI document declares a bearer scheme while Foreplay's own integration
    guides show the key sent bare, so both are attempted rather than guessed at.
    """
    query = urllib.parse.urlencode(
        {name: value for name, value in params.items() if value is not None}
    )
    url = f"{BASE_URL}{path}?{query}"
    last_error: Exception | None = None
    for header in (f"Bearer {key}", key):
        appeal = urllib.request.Request(url, headers={"Authorization": header})
        try:
            with urllib.request.urlopen(appeal, timeout=TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code not in (401, 403):
                raise
    raise SystemExit(f"Foreplay rejected the API key for {path}: {last_error}")


def fetch_board(board_id: str, key: str) -> list[dict]:
    ads: list[dict] = []
    cursor = None
    while True:
        payload = request(
            BOARD_ADS,
            key,
            {
                "board_id": board_id,
                "limit": PAGE_LIMIT,
                "order": "longest_running",
                "cursor": cursor,
            },
        )
        page = payload.get("data") or []
        ads.extend(page)
        cursor = (payload.get("metadata") or {}).get("cursor")
        if not cursor or not page:
            return ads


def fetch_brands(board_id: str, key: str) -> dict[str, dict]:
    payload = request(BOARD_BRANDS, key, {"board_id": board_id, "limit": PAGE_LIMIT})
    brands = {}
    for brand in payload.get("data") or []:
        identifier = brand.get("id")
        if not identifier:
            continue
        websites = brand.get("websites") or []
        brands[identifier] = {
            "id": identifier,
            "name": brand.get("name"),
            "category": brand.get("category"),
            "site": websites[0] if websites else None,
        }
    return brands


def awareness_from(duration: float | None, mentioned_at: float | None) -> dict:
    """Awareness proxy from how long an ad runs before naming the product.

    A cold opening withholds the product; a product-aware opening leads with it.
    This is a strong first-pass sort, not ground truth: an ad can name the product
    immediately and still address an unaware buyer, so every value needs review.
    """
    if mentioned_at is None or not duration:
        return {"code": None, "mention_ratio": None, "basis": "unavailable"}
    if mentioned_at < 0:
        return {"code": "UWA", "mention_ratio": -1.0, "basis": "mention-ratio"}
    ratio = round(mentioned_at / duration, 4)
    if ratio >= 0.75:
        code = "UWA"
    elif ratio >= 0.45:
        code = "PRA"
    elif ratio >= 0.20:
        code = "SLA"
    else:
        code = "PDA"
    return {"code": code, "mention_ratio": ratio, "basis": "mention-ratio"}


def opening_seconds(segments: object, limit: float = 3.0) -> list[dict] | None:
    if not isinstance(segments, list):
        return None
    kept = []
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        start = segment.get("start", segment.get("start_time", segment.get("from")))
        try:
            if start is not None and float(start) > limit:
                break
        except (TypeError, ValueError):
            pass
        kept.append(segment)
    return kept or None


def to_entry(ad: dict, brands: dict[str, dict], board_name: str) -> dict:
    duration = ad.get("video_duration")
    mentioned_at = ad.get("time_product_was_mentioned")
    running = ad.get("running_duration") or {}
    brand_id = ad.get("brand_id") or ""
    brand = brands.get(brand_id, {"id": brand_id, "name": None, "category": None, "site": None})

    display = (ad.get("display_format") or "unknown").lower()
    headline = ad.get("headline") or None
    primary_text = ad.get("description") or None
    transcription = ad.get("full_transcription") or None
    annotatable = bool(headline or primary_text or transcription)

    return {
        "id": ad.get("id") or ad.get("ad_id"),
        "ad_id": ad.get("ad_id"),
        "foreplay_url": ad.get("foreplay_url"),
        "source": "curated-board",
        "board": board_name,
        "brand": brand,
        "format": display if display in FORMATS else "unknown",
        "product_category": ad.get("product_category") or None,
        "niches": [n for n in (ad.get("niches") or []) if isinstance(n, str)],
        "evidence": {
            "running_days": running.get("days"),
            "live": ad.get("live"),
            "started_running": ad.get("started_running"),
            "video_duration_seconds": duration,
            "product_mentioned_at_seconds": mentioned_at,
            "class": "behavioural",
        },
        "awareness": awareness_from(duration, mentioned_at),
        "content": {
            "headline": headline,
            "primary_text": primary_text,
            "transcription": transcription,
            "opening_seconds": opening_seconds(ad.get("timestamped_transcription")),
        },
        "annotation": None,
        "annotatable": annotatable,
        "annotatable_blocker": None
        if annotatable
        else "Foreplay returned no headline, primary text or transcript for this ad",
        "reviewed": False,
    }


def merge(existing: list[dict], fetched: list[dict]) -> tuple[list[dict], dict[str, int]]:
    """Refresh fetched fields and never discard a human annotation or review."""
    by_id = {entry.get("id"): entry for entry in existing}
    counts = {"added": 0, "refreshed": 0, "annotations_kept": 0}
    merged: list[dict] = []
    for entry in fetched:
        previous = by_id.pop(entry["id"], None)
        if previous is None:
            counts["added"] += 1
            merged.append(entry)
            continue
        counts["refreshed"] += 1
        if previous.get("annotation"):
            entry["annotation"] = previous["annotation"]
            entry["reviewed"] = previous.get("reviewed", False)
            counts["annotations_kept"] += 1
        merged.append(entry)
    # Entries no longer on the board are retained: removing one would silently
    # discard reviewed annotation work.
    merged.extend(by_id.values())
    merged.sort(key=lambda e: -((e.get("evidence") or {}).get("running_days") or 0))
    return merged, counts


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board-id", required=True)
    parser.add_argument("--board-name", default="best_ads")
    parser.add_argument(
        "--from-file",
        type=pathlib.Path,
        help="read a saved API payload instead of calling Foreplay, for offline tests",
    )
    args = parser.parse_args(argv[1:])

    if args.from_file:
        payload = json.loads(args.from_file.read_text())
        ads = payload.get("ads", payload if isinstance(payload, list) else [])
        brands = payload.get("brands", {}) if isinstance(payload, dict) else {}
    else:
        key = os.environ.get("FOREPLAY_API_KEY")
        if not key:
            print(
                "FOREPLAY_API_KEY is not set. Add it as a repository secret for CI, "
                "or export it locally.",
                file=sys.stderr,
            )
            return 2
        ads = fetch_board(args.board_id, key)
        brands = fetch_brands(args.board_id, key)

    fetched = [to_entry(ad, brands, args.board_name) for ad in ads if ad.get("id") or ad.get("ad_id")]
    existing = json.loads(ENTRIES.read_text())["entries"] if ENTRIES.is_file() else []
    merged, counts = merge(existing, fetched)

    ENTRIES.parent.mkdir(parents=True, exist_ok=True)
    ENTRIES.write_text(
        json.dumps(
            {
                "schema": "schemas/swipe-entry.schema.json",
                "entries": merged,
            },
            indent=1,
            ensure_ascii=False,
        )
        + "\n"
    )

    annotatable = sum(1 for e in merged if e.get("annotatable"))
    reviewed = sum(1 for e in merged if e.get("reviewed"))
    print(
        f"{len(merged)} entries: {counts['added']} added, {counts['refreshed']} refreshed, "
        f"{counts['annotations_kept']} annotations kept"
    )
    print(f"{annotatable} annotatable, {reviewed} reviewed")
    print("Run scripts/build-swipe-digest.py to regenerate the routed digest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
