"""Tests for the eval harness.

The model transport is stubbed. These check the pipeline, the rubric wiring and the
failure behaviour without a key, not the quality of any model's output.
"""

import contextlib
import importlib.util
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"


def load(name):
    path = EVALS / f"{name}.py"
    if not path.exists():
        raise AssertionError(f"{path} should exist")
    spec = importlib.util.spec_from_file_location(f"evals_{name}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RubricTests(unittest.TestCase):
    def test_every_criterion_is_documented_and_scored_out_of_two(self):
        rubric = load("rubric")

        self.assertEqual(len(rubric.CRITERIA) * 2, rubric.MAX_SCORE)
        for key, description in rubric.CRITERIA:
            with self.subTest(key=key):
                self.assertRegex(key, r"^[a-z_]+$")
                self.assertGreater(len(description), 30)

    def test_the_rubric_covers_the_hook_quality_standard(self):
        rubric = load("rubric")
        keys = {key for key, _ in rubric.CRITERIA}

        # The three non-negotiables and the opening-type declaration from
        # references/20-hook-quality-standard.md must each be scored.
        for required in (
            "opening_type",
            "must_have_carriers",
            "no_prior_context",
            "starts_in_action",
            "no_chaos",
            "body_handoff",
        ):
            self.assertIn(required, keys)

    def test_the_rubric_scores_marking_rather_than_penalising_thin_input(self):
        rubric = load("rubric")
        prompt = rubric.judge_prompt("a brief", "some output")

        self.assertIn("placeholder_discipline", prompt)
        self.assertIn("do not penalise a marked placeholder", prompt)

    def test_judge_prompt_carries_the_brief_and_the_output(self):
        rubric = load("rubric")

        prompt = rubric.judge_prompt("BRIEF-MARKER", "OUTPUT-MARKER")

        self.assertIn("BRIEF-MARKER", prompt)
        self.assertIn("OUTPUT-MARKER", prompt)
        self.assertIn("JSON only", prompt)


class RunnerTests(unittest.TestCase):
    def test_exits_with_guidance_when_the_key_is_absent(self):
        run = load("run")

        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SystemExit) as raised:
                run.main(["run.py", "--out", "/tmp/unused.json"])

        self.assertIn("ANTHROPIC_API_KEY is not set", str(raised.exception))

    def test_briefs_exist_and_declare_an_awareness_target(self):
        briefs = sorted((EVALS / "briefs").glob("*.md"))

        self.assertGreaterEqual(len(briefs), 6)
        for path in briefs:
            with self.subTest(brief=path.stem):
                text = path.read_text().lower()
                self.assertIn("awareness target", text)
                self.assertIn("deliverable", text)

    def test_briefs_carry_no_private_commercial_data(self):
        # Fixtures are built from public product information on purpose.
        for path in sorted((EVALS / "briefs").glob("*.md")):
            with self.subTest(brief=path.stem):
                text = path.read_text()
                self.assertNotIn("api_key", text.lower())
                self.assertNotIn("secret", text.lower())

    def test_total_sums_only_recognised_criteria(self):
        run = load("run")
        rubric = load("rubric")
        keys = [key for key, _ in rubric.CRITERIA]
        verdict = {
            "scores": {
                **{key: {"score": 2} for key in keys},
                "invented_criterion": {"score": 2},
            }
        }

        self.assertEqual(rubric.MAX_SCORE, run.total(verdict))

    def test_total_tolerates_a_partial_verdict(self):
        run = load("run")
        rubric = load("rubric")
        first = rubric.CRITERIA[0][0]

        self.assertEqual(1, run.total({"scores": {first: {"score": 1}}}))
        self.assertIsNone(run.total({"scores": "not a mapping"}))
        self.assertIsNone(run.total({}))

    def test_parse_scores_recovers_json_wrapped_in_prose(self):
        run = load("run")

        parsed = run.parse_scores('Sure, here you go:\n{"scores": {"a": 1}}\nHope that helps.')

        self.assertEqual({"scores": {"a": 1}}, parsed)

    def test_parse_scores_reports_a_non_json_reply(self):
        run = load("run")

        parsed = run.parse_scores("I would rather not.")

        self.assertIn("error", parsed)

    def test_run_writes_a_result_file_with_a_stubbed_transport(self):
        run = load("run")
        rubric = load("rubric")
        verdict = json.dumps(
            {"scores": {key: {"score": 2, "reason": "fine"} for key, _ in rubric.CRITERIA}}
        )
        replies = ["generated hook options", verdict]

        with tempfile.TemporaryDirectory() as directory:
            out = pathlib.Path(directory) / "result.json"
            with mock.patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test"}):
                with mock.patch.object(run, "complete", side_effect=lambda *a, **k: replies.pop(0)):
                    run.main(
                        [
                            "run.py",
                            "--out",
                            str(out),
                            "--brief",
                            "grounding-sheet-thin",
                        ]
                    )
            payload = json.loads(out.read_text())

        self.assertEqual(1, payload["briefs"])
        self.assertEqual(rubric.MAX_SCORE, payload["results"][0]["total"])
        self.assertEqual(float(rubric.MAX_SCORE), payload["mean"])

    def test_generation_prompt_forbids_inventing_and_refusing(self):
        run = load("run")

        prompt = run.generation_prompt("a brief", "context")

        self.assertIn("Never invent a specific", prompt)
        self.assertIn("Never refuse for thin input", prompt)
        self.assertIn("minimum three", prompt)

    def test_generation_context_uses_the_whole_craft_stack(self):
        run = load("run")
        validator_stack = run.CRAFT_STACK

        for relative in validator_stack:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())
        self.assertGreaterEqual(len(validator_stack), 12)


class ReportTests(unittest.TestCase):
    def make_run(self, mean, score):
        rubric = load("rubric")
        return {
            "model": "m",
            "judge_model": "m",
            "briefs": 1,
            "mean": mean,
            "max": rubric.MAX_SCORE,
            "results": [
                {
                    "brief": "greens-powder-cold",
                    "total": score,
                    "max": rubric.MAX_SCORE,
                    "verdict": {
                        "scores": {
                            key: {"score": 1} for key, _ in rubric.CRITERIA
                        }
                    },
                }
            ],
        }

    def test_criterion_means_average_each_criterion(self):
        report = load("report")
        rubric = load("rubric")

        means = report.criterion_means(self.make_run(10.0, 10))

        self.assertEqual(len(rubric.CRITERIA), len(means))
        self.assertTrue(all(value == 1.0 for value in means.values()))

    def test_comparing_two_runs_prints_a_delta(self):
        report = load("report")
        with tempfile.TemporaryDirectory() as directory:
            before = pathlib.Path(directory) / "before.json"
            after = pathlib.Path(directory) / "after.json"
            before.write_text(json.dumps(self.make_run(8.0, 8)))
            after.write_text(json.dumps(self.make_run(14.0, 14)))

            with mock.patch("sys.stdout"):
                code = report.main(["report.py", str(before), str(after)])

        self.assertEqual(0, code)

    def compare_output(self, before_run, after_run):
        report = load("report")
        with tempfile.TemporaryDirectory() as directory:
            before = pathlib.Path(directory) / "before.json"
            after = pathlib.Path(directory) / "after.json"
            before.write_text(json.dumps(before_run))
            after.write_text(json.dumps(after_run))
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = report.main(["report.py", str(before), str(after)])
        self.assertEqual(0, code)
        return buffer.getvalue().split("=== comparison ===", 1)[1]

    def test_same_scale_runs_still_report_a_plain_delta(self):
        output = self.compare_output(self.make_run(8.0, 8), self.make_run(14.0, 14))

        self.assertIn("+6.00, better", output)
        self.assertNotIn("RUBRIC CHANGED", output)

    def test_a_changed_rubric_refuses_to_subtract_across_scales(self):
        # The failure this prevents: 18/20 against 32/36 printing "+14.00, better", or a
        # genuinely poor 17/36 printing "-1.00, worse" and reading as a minor wobble.
        old = self.make_run(18.0, 18)
        old["max"] = 20
        old["results"][0]["max"] = 20
        new = self.make_run(32.0, 32)
        new["max"] = 36
        new["results"][0]["max"] = 36

        output = self.compare_output(old, new)

        self.assertIn("RUBRIC CHANGED", output)
        self.assertIn("out of 20 before and 36 after", output)
        self.assertIn("90.0%", output)
        self.assertIn("88.9%", output)
        self.assertNotIn("+14.00", output)

    def test_criteria_absent_from_the_baseline_are_listed_separately(self):
        rubric = load("rubric")
        old = self.make_run(8.0, 8)
        dropped = rubric.CRITERIA[-1][0]
        del old["results"][0]["verdict"]["scores"][dropped]

        output = self.compare_output(old, self.make_run(14.0, 14))

        self.assertIn("no before", output)
        self.assertIn(dropped, output.split("no before", 1)[1])


if __name__ == "__main__":
    unittest.main()
