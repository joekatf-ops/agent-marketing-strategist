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
    _inside,
    _require_no_symlink_components,
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
    try:
        if stat.S_ISLNK(os.lstat(path).st_mode):
            raise OSError("audit target must not be a symlink")
    except FileNotFoundError:
        pass
    flags = os.O_WRONLY | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o644)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise OSError("audit target must be one regular, unlinked path")
        os.ftruncate(descriptor, 0)
        audit_file = os.fdopen(descriptor, "w", encoding="utf-8")
        descriptor = -1
        with audit_file:
            audit_file.write(content)
    finally:
        if descriptor >= 0:
            os.close(descriptor)


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
        try:
            _require_no_symlink_components(brand_folder)
            _require_no_symlink_components(run_folder)
            safe_run = _inside(run_folder, brand_folder) and run_folder.is_dir()
        except ValueError:
            safe_run = False
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
