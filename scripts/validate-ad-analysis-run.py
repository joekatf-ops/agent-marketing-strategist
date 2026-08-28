#!/usr/bin/env python3
"""Validate one brand-scoped ad-analysis intake and optionally write its audit."""

from __future__ import annotations

import argparse
import os
import pathlib
import secrets
import stat
import sys

from ad_analysis_harness import (
    _absolute_lexical,
    _no_follow_flag,
    _open_directory_no_follow,
    _open_validation_session,
    _redact_credentials,
    _validate_session,
    _validate_run_id,
    render_input_audit,
    validate_run,
)


def _diagnostic(message: str) -> None:
    content = (_redact_credentials(message) + "\n").encode(
        "utf-8", errors="backslashreplace"
    )
    sys.stdout.buffer.write(content)
    sys.stdout.buffer.flush()


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


def _audit_file_identity(
    metadata: os.stat_result,
) -> tuple[int, int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
        metadata.st_nlink,
    )


def _audit_destination_identity(
    directory_descriptor: int, filename: str
) -> tuple[int, int, int, int, int, int] | None:
    try:
        metadata = os.stat(
            filename,
            dir_fd=directory_descriptor,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise OSError("audit target must be one regular, single-link path")
    return _audit_file_identity(metadata)


def _write_all(descriptor: int, content: bytes) -> None:
    remaining = memoryview(content)
    while remaining:
        written = os.write(descriptor, remaining)
        if written <= 0:
            raise OSError("failed to write staged input audit")
        remaining = remaining[written:]


def _verified_audit_descriptor(
    descriptor: int, content: bytes
) -> os.stat_result | None:
    before = os.fstat(descriptor)
    if (
        not stat.S_ISREG(before.st_mode)
        or before.st_nlink != 1
        or before.st_size != len(content)
    ):
        return None
    offset = 0
    while offset < len(content):
        chunk = os.pread(
            descriptor, min(1024 * 1024, len(content) - offset), offset
        )
        if not chunk or chunk != content[offset : offset + len(chunk)]:
            return None
        offset += len(chunk)
    if os.pread(descriptor, 1, offset):
        return None
    after = os.fstat(descriptor)
    if _audit_file_identity(after) != _audit_file_identity(before):
        return None
    return after


def _published_audit_is_verified(
    directory_descriptor: int,
    filename: str,
    staging_descriptor: int,
    content: bytes,
) -> bool:
    descriptor_state = _verified_audit_descriptor(staging_descriptor, content)
    if descriptor_state is None:
        return False
    try:
        destination = os.stat(
            filename,
            dir_fd=directory_descriptor,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        return False
    final_descriptor_state = os.fstat(staging_descriptor)
    return (
        stat.S_ISREG(destination.st_mode)
        and destination.st_nlink == 1
        and _audit_file_identity(final_descriptor_state)
        == _audit_file_identity(descriptor_state)
        and _audit_file_identity(destination)
        == _audit_file_identity(descriptor_state)
    )


def _remove_unverified_failed_audit(
    directory_descriptor: int,
    filename: str,
    original_destination: tuple[int, int, int, int, int, int] | None,
    staging_descriptor: int,
    content: bytes,
) -> None:
    try:
        current = os.stat(
            filename,
            dir_fd=directory_descriptor,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        return
    if (
        original_destination is not None
        and _audit_file_identity(current) == original_destination
    ):
        return
    if _published_audit_is_verified(
        directory_descriptor, filename, staging_descriptor, content
    ):
        return
    os.unlink(filename, dir_fd=directory_descriptor)
    try:
        os.stat(filename, dir_fd=directory_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        os.fsync(directory_descriptor)
        return
    raise OSError("unverified input audit could not be removed")


def _write_input_audit(path: pathlib.Path, content: str, *, session=None) -> None:
    encoded_content = content.encode("utf-8", errors="backslashreplace")
    path = _absolute_lexical(path)
    no_follow = _no_follow_flag()
    if session is not None:
        if path.parent != session.run_folder or not session.is_current():
            raise OSError("validated run identity changed before audit publication")
        directory_descriptor = os.dup(session.run_descriptor)
    else:
        directory_descriptor = _open_directory_no_follow(path.parent)
    temporary_name = ""
    descriptor = -1
    initial_destination: tuple[int, int, int, int, int, int] | None = None
    publication_attempted = False
    try:
        initial_destination = _audit_destination_identity(
            directory_descriptor, path.name
        )
        for _ in range(1000):
            candidate = f".{path.name}.tmp-{secrets.token_hex(16)}"
            try:
                descriptor = os.open(
                    candidate,
                    os.O_RDWR | os.O_CREAT | os.O_EXCL | no_follow,
                    0o600,
                    dir_fd=directory_descriptor,
                )
            except FileExistsError:
                continue
            temporary_name = candidate
            break
        if descriptor < 0:
            raise OSError("could not allocate a private audit staging file")
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise OSError("audit staging file must be regular and single-link")
        _write_all(descriptor, encoded_content)
        os.fsync(descriptor)
        staged = _verified_audit_descriptor(descriptor, encoded_content)
        if staged is None or (
            staged.st_dev != metadata.st_dev or staged.st_ino != metadata.st_ino
        ):
            raise OSError("audit staging file changed before publication")

        if session is not None and not session.is_current():
            raise OSError("validated run identity changed before audit publication")
        if (
            _audit_destination_identity(directory_descriptor, path.name)
            != initial_destination
        ):
            raise OSError("audit destination changed before publication")
        current_staging = os.stat(
            temporary_name,
            dir_fd=directory_descriptor,
            follow_symlinks=False,
        )
        if _audit_file_identity(current_staging) != _audit_file_identity(staged):
            raise OSError("audit staging file changed before publication")
        publication_attempted = True
        os.replace(
            temporary_name,
            path.name,
            src_dir_fd=directory_descriptor,
            dst_dir_fd=directory_descriptor,
        )
        if not _published_audit_is_verified(
            directory_descriptor,
            path.name,
            descriptor,
            encoded_content,
        ):
            raise OSError("published input audit identity or content is unsafe")
        os.fsync(directory_descriptor)
        temporary_name = ""
    except BaseException:
        if publication_attempted and descriptor >= 0:
            _remove_unverified_failed_audit(
                directory_descriptor,
                path.name,
                initial_destination,
                descriptor,
                encoded_content,
            )
        raise
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary_name:
            try:
                os.unlink(temporary_name, dir_fd=directory_descriptor)
            except FileNotFoundError:
                pass
        os.close(directory_descriptor)


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
    session = None
    try:
        session = _open_validation_session(args.brand, args.run)
    except (FileNotFoundError, OSError, ValueError):
        result = validate_run(args.brand, args.run)
    else:
        result = _validate_session(session)
    audit_write_failed = False
    try:
        _diagnostic(f"Input readiness: {result.status}")
        for error in result.errors:
            _diagnostic(f"Error: {error}")
        for limitation in result.limitations:
            _diagnostic(f"Limitation: {limitation}")

        if args.write_audit and session is not None:
            audit_path = session.run_folder / "input-audit.md"
            try:
                content = render_input_audit(session.intake, result)
                _write_input_audit(audit_path, content, session=session)
            except OSError:
                audit_write_failed = True
                _diagnostic(
                    "Error: input audit was not written because its target is unsafe"
                )
            else:
                _diagnostic(f"Input audit: {audit_path}")
        elif args.write_audit:
            audit_write_failed = True
            _diagnostic(
                "Error: input audit was not written because the run folder is unsafe"
            )
    finally:
        if session is not None:
            session.close()

    return 1 if result.status == "blocked" or audit_write_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
