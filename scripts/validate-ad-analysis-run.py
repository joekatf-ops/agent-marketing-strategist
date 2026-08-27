#!/usr/bin/env python3
"""Validate one brand-scoped ad-analysis intake and optionally write its audit."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import stat

from ad_analysis_harness import (
    _absolute_lexical,
    _no_follow_flag,
    _open_directory_no_follow,
    _validate_run_id,
    load_intake,
    render_input_audit,
    validate_run,
)


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brand", type=pathlib.Path, help="brand folder")
    parser.add_argument("run", type=pathlib.Path, help="ad-analysis run folder")
    parser.add_argument(
        "--write-audit",
        action="store_true",
        help="write input-audit.md inside the validated run folder",
    )
    return parser.parse_args()


def _write_input_audit(path: pathlib.Path, content: str) -> None:
    encoded_content = content.encode("utf-8", errors="backslashreplace")
    path = _absolute_lexical(path)
    no_follow = _no_follow_flag()
    directory_descriptor = _open_directory_no_follow(path.parent)
    try:
        descriptor = os.open(
            path.name,
            os.O_WRONLY | os.O_CREAT | no_follow,
            0o644,
            dir_fd=directory_descriptor,
        )
    finally:
        os.close(directory_descriptor)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise OSError("audit target must be one regular, unlinked path")
        os.ftruncate(descriptor, 0)
        audit_file = os.fdopen(descriptor, "wb")
        descriptor = -1
        with audit_file:
            audit_file.write(encoded_content)
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _is_canonical_run_folder(
    brand_folder: pathlib.Path, run_folder: pathlib.Path
) -> bool:
    brand_folder = _absolute_lexical(brand_folder)
    run_folder = _absolute_lexical(run_folder)
    if run_folder.parent != brand_folder / "outputs" / "ad-analysis":
        return False
    try:
        _validate_run_id(run_folder.name)
        descriptor = _open_directory_no_follow(run_folder)
    except (FileNotFoundError, OSError, ValueError):
        return False
    os.close(descriptor)
    return True


def main() -> int:
    args = _arguments()
    result = validate_run(args.brand, args.run)
    print(f"Input readiness: {result.status}")
    for error in result.errors:
        print(f"Error: {error}")
    for limitation in result.limitations:
        print(f"Limitation: {limitation}")

    audit_write_failed = False
    if args.write_audit:
        brand_folder = _absolute_lexical(args.brand)
        run_folder = _absolute_lexical(args.run)
        safe_run = _is_canonical_run_folder(brand_folder, run_folder)
        if safe_run:
            try:
                intake = load_intake(run_folder)
            except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError):
                intake = {}
            audit_path = run_folder / "input-audit.md"
            try:
                _write_input_audit(audit_path, render_input_audit(intake, result))
            except OSError:
                audit_write_failed = True
                print("Error: input audit was not written because its target is unsafe")
            else:
                print(f"Input audit: {audit_path}")
        else:
            audit_write_failed = True
            print("Error: input audit was not written because the run folder is unsafe")

    return 1 if result.status == "blocked" or audit_write_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
