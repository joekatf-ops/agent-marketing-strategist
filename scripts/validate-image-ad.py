#!/usr/bin/env python3
"""Validate an image-ad run and measure local PNG/JPEG/WebP dimensions.
Usage: python3 scripts/validate-image-ad.py path/to/run.json
No network calls. Text, claims, product fidelity and design still require actual inspection.
"""
import argparse
import json
import pathlib
import re
import struct

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas/image-ad-run.schema.json"
MARKER = re.compile(r"\[(?:CLAIM|PROOF|PRICE|STAT|MECHANISM)\s*:", re.I)


def dimensions(path):
    """Read raster headers, not a filename or the requested generation ratio."""
    data = pathlib.Path(path).read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 33 and data[12:16] == b"IHDR":
        size = struct.unpack(">II", data[16:24])
    elif data[:2] == b"\xff\xd8":
        i, size = 2, None
        while i < len(data):
            if data[i] != 255:
                raise ValueError("malformed JPEG marker")
            while i < len(data) and data[i] == 255:
                i += 1
            if i >= len(data):
                break
            marker = data[i]
            i += 1
            if marker in (0xD9, 0xDA):
                break
            if marker == 1 or 0xD0 <= marker <= 0xD8:
                continue
            if i + 2 > len(data):
                break
            length = int.from_bytes(data[i:i + 2], "big")
            if length < 2 or i + length > len(data):
                raise ValueError("truncated JPEG segment")
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                if length < 8:
                    raise ValueError("invalid JPEG frame")
                height, width = struct.unpack(">HH", data[i + 3:i + 7])
                size = (width, height)
                break
            i += length
        if size is None:
            raise ValueError("JPEG dimensions unavailable")
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        kind = data[12:16]
        if kind == b"VP8X" and len(data) >= 30:
            size = (1 + int.from_bytes(data[24:27], "little"),
                    1 + int.from_bytes(data[27:30], "little"))
        elif kind == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
            bits = int.from_bytes(data[21:25], "little")
            size = ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
        elif kind == b"VP8 " and len(data) >= 30 and data[23:26] == b"\x9d\x01\x2a":
            width, height = struct.unpack("<HH", data[26:30])
            size = (width & 0x3FFF, height & 0x3FFF)
        else:
            raise ValueError("unsupported or truncated WebP header")
    else:
        raise ValueError("not a supported PNG, JPEG or WebP")
    if min(size) < 1:
        raise ValueError("empty dimensions")
    return size


def schema_errors(value, schema, path="$"):
    """Evaluate the structural keywords used by this package's run schema."""
    errors = []
    kinds = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}
    kind = schema.get("type")
    if kind and (not isinstance(value, kinds[kind]) or kind == "integer" and isinstance(value, bool)):
        return [f"{path}: expected {kind}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: unsupported value")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or not value.strip():
            errors.append(f"{path}: empty string")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: invalid format")
    if kind == "integer" and value < schema.get("minimum", value):
        errors.append(f"{path}: below minimum")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing {key}")
        props = schema.get("properties", {})
        for key, item in value.items():
            if key in props:
                errors.extend(schema_errors(item, props[key], f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unknown field {key}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: too few items")
        for i, item in enumerate(value):
            errors.extend(schema_errors(item, schema.get("items", {}), f"{path}[{i}]"))
    return errors


def validate(record, base):
    errors = schema_errors(record, json.loads(SCHEMA.read_text()))
    if errors:
        return errors
    seen_indices, seen_jobs = set(), set()
    for item in record["outputs"]:
        label = f"output {item['index']}"
        if item["index"] in seen_indices:
            errors.append(f"{label}: duplicate index")
        seen_indices.add(item["index"])
        job = item.get("job_id")
        if job and job in seen_jobs:
            errors.append(f"{label}: duplicate job ID")
        if job:
            seen_jobs.add(job)
        if MARKER.search(item["copy_on_image"]) or MARKER.search(item["prompt"]):
            errors.append(f"{label}: missing-fact marker in production copy or prompt")
        status = item["status"]
        local = item.get("file")
        if status in ("generated", "verified") and not (local or item.get("result_url")):
            errors.append(f"{label}: generated output has no actual asset")
        if status == "verified" and not local:
            errors.append(f"{label}: local verification requires a file; remote checks must be recorded separately")
        if local:
            path = pathlib.Path(local)
            if not path.is_absolute():
                path = pathlib.Path(base) / path
            try:
                width, height = dimensions(path)
                ratio_width, ratio_height = map(int, item["aspect_ratio"].split(":"))
                if width * ratio_height != height * ratio_width:
                    errors.append(f"{label}: actual image is {width}x{height}, not {item['aspect_ratio']}")
                if (item.get("width", width), item.get("height", height)) != (width, height):
                    errors.append(f"{label}: recorded dimensions disagree with actual file")
            except (OSError, ValueError, struct.error) as exc:
                errors.append(f"{label}: unreadable image: {exc}")
        if status == "verified":
            if "width" not in item or "height" not in item:
                errors.append(f"{label}: verified output must record measured dimensions")
            checks = item.get("checks", {})
            if not all(checks.get(key) is True for key in ("text", "product", "layout", "claims")):
                errors.append(f"{label}: verified output requires recorded inspection of text, product, layout and claims")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=pathlib.Path)
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text())
        errors = validate(record, args.record.parent)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print("Image-ad record valid. Header checks do not replace visual inspection or prove performance.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
