#!/usr/bin/env python3
"""Summarise one eval result, or compare two.

    python3 evals/report.py evals/results/2026-08-31.json
    python3 evals/report.py evals/results/before.json evals/results/after.json

Comparing two runs is the useful mode. The absolute value of an LLM-judged rubric
drifts with the judge, so a difference between runs scored the same way says more
than either number alone.
"""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import rubric  # noqa: E402


def load(path: pathlib.Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"{path} not found")
    return json.loads(path.read_text())


def criterion_means(run: dict) -> dict[str, float]:
    sums: dict[str, list[int]] = {key: [] for key, _ in rubric.CRITERIA}
    for result in run["results"]:
        entries = (result.get("verdict") or {}).get("scores")
        if not isinstance(entries, dict):
            continue
        for key, _ in rubric.CRITERIA:
            item = entries.get(key)
            if isinstance(item, dict) and isinstance(item.get("score"), int):
                sums[key].append(item["score"])
    return {
        key: round(sum(values) / len(values), 2)
        for key, values in sums.items()
        if values
    }


def summarise(run: dict, path: pathlib.Path) -> None:
    print(f"=== {path.name} ===")
    print(f"model {run.get('model')}, judge {run.get('judge_model')}")
    print(f"mean {run.get('mean')} / {run.get('max')} across {run.get('briefs')} briefs\n")
    print(f"{'criterion':26} {'mean of 2':>9}")
    print("-" * 37)
    for key, mean in criterion_means(run).items():
        flag = "  <-- weakest" if mean < 1.0 else ""
        print(f"{key:26} {mean:>9}{flag}")
    print()
    print(f"{'brief':30} {'score':>7}")
    print("-" * 39)
    for result in run["results"]:
        print(f"{result['brief']:30} {str(result.get('total')):>3}/{result.get('max')}")


def compare(before: dict, after: dict) -> None:
    print("\n=== comparison ===")

    # The rubric grows. When it does, the two runs are scored out of different totals and a
    # raw delta is nonsense: 18/20 against 32/36 would print "+14.00, better". Per-criterion
    # means stay comparable for the criteria present on both sides, so those carry the
    # comparison and the totals are shown as percentages with the mismatch named.
    before_max, after_max = before.get("max"), after.get("max")
    rescaled = (
        isinstance(before_max, (int, float))
        and isinstance(after_max, (int, float))
        and before_max != after_max
    )

    before_mean, after_mean = before.get("mean"), after.get("mean")
    if isinstance(before_mean, (int, float)) and isinstance(after_mean, (int, float)):
        if rescaled:
            before_pct = 100 * before_mean / before_max
            after_pct = 100 * after_mean / after_max
            print(
                f"RUBRIC CHANGED: scored out of {before_max} before and {after_max} after, "
                "so the totals are not directly comparable."
            )
            print(
                f"mean {before_mean}/{before_max} ({before_pct:.1f}%) -> "
                f"{after_mean}/{after_max} ({after_pct:.1f}%)"
            )
            print(
                "Read the per-criterion table below instead. A percentage across different "
                "criteria is not a like-for-like measurement either: the added criteria may "
                "simply be harder or easier than the ones they joined.\n"
            )
        else:
            delta = after_mean - before_mean
            direction = "better" if delta > 0 else "worse" if delta < 0 else "unchanged"
            print(f"mean {before_mean} -> {after_mean}  ({delta:+.2f}, {direction})\n")

    left, right = criterion_means(before), criterion_means(after)
    print(f"{'criterion':26} {'before':>7} {'after':>7} {'delta':>7}")
    print("-" * 51)
    unmatched = []
    for key, _ in rubric.CRITERIA:
        if key not in left or key not in right:
            if key in right:
                unmatched.append(key)
            continue
        delta = right[key] - left[key]
        print(f"{key:26} {left[key]:>7} {right[key]:>7} {delta:>+7.2f}")

    if unmatched:
        print(f"\n{'criterion (new, no before)':26} {'after':>7}")
        print("-" * 35)
        for key in unmatched:
            print(f"{key:26} {right[key]:>7}")

    by_brief = {r["brief"]: r.get("total") for r in before["results"]}
    suffix = f" (of {before_max} / {after_max})" if rescaled else ""
    print(f"\n{'brief':30} {'before':>7} {'after':>7}{suffix}")
    print("-" * 46)
    for result in after["results"]:
        was = by_brief.get(result["brief"])
        print(f"{result['brief']:30} {str(was):>7} {str(result.get('total')):>7}")


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3):
        print(__doc__)
        return 2
    paths = [pathlib.Path(a) for a in argv[1:]]
    runs = [load(p) for p in paths]
    for run, path in zip(runs, paths):
        summarise(run, path)
        print()
    if len(runs) == 2:
        compare(runs[0], runs[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
