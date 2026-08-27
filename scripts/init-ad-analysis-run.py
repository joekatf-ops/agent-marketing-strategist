#!/usr/bin/env python3
"""Create a portable ad-analysis run for one local brand folder."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from ad_analysis_harness import initialise_run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brand_folder", type=pathlib.Path)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--market", required=True)
    parser.add_argument("--run-id")
    args = parser.parse_args()
    try:
        run_folder = initialise_run(
            brand_folder=args.brand_folder,
            mode=args.mode,
            product_id=args.product_id,
            market=args.market,
            run_id=args.run_id,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(run_folder)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
