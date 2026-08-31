"""Tests for the sixteen copywriting standards and the lexicon that enforces two of them.

The standard itself is prose and mostly checked by reading. What is checked here is the
machinery around it: that the lexicon parses, that the checker actually detects rather than
passing vacuously, that the frozen examples are clean, and that the rules with a mechanical
or eval home are wired to it.
"""

import importlib.util
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
STANDARD = ROOT / "references" / "26-copywriting-standards.md"
LEXICON = ROOT / "config" / "copy-lexicon.yml"
CHECKER = ROOT / "scripts" / "check-copy-lexicon.py"

# The sixteen, in the order they appear on the source list.
RULES = (
    "Sell the end state",
    "Pass the stranger test",
    "Cut, then cut again",
    "Select your reader",
    "No em dashes",
    "Tone matches slot",
    "Kill empty hedges",
    "Angles, not synonyms",
    "One idea each",
    "Never invent claims",
    "Truth beats style",
    "Benefit, not mechanism",
    "Numbers beat adjectives",
    "Front-load the point",
    "Sound unmistakably brand",
    "No AI lexicon",
)

CONTRACTS_WITH_LEXICON_CHECK = (
    "contracts/ad-copy.md",
    "contracts/hook-batch.md",
    "contracts/video-script.md",
    "contracts/static-spec.md",
)


def load_checker():
    spec = importlib.util.spec_from_file_location("check_copy_lexicon", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checker(*args):
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


class StandardTests(unittest.TestCase):
    def test_standard_exists_and_states_all_sixteen(self):
        self.assertTrue(STANDARD.is_file(), "references/26-copywriting-standards.md should exist")
        text = STANDARD.read_text(encoding="utf-8")
        for index, rule in enumerate(RULES, start=1):
            with self.subTest(rule=rule):
                self.assertIn(f"### {index}. {rule}", text)

    def test_standard_declares_a_precedence_order(self):
        text = STANDARD.read_text(encoding="utf-8")
        self.assertIn("Precedence, when two of them collide", text)
        # Never inventing a claim has to outrank the rules that tempt invention, notably
        # "numbers beat adjectives". If that ordering is ever lost the eval regression that
        # produced an invented statistic becomes reachable again.
        precedence = text.split("Precedence, when two of them collide", 1)[1]
        precedence = precedence.split("## The sixteen", 1)[0]
        self.assertIn("Never invent a claim", precedence)
        self.assertLess(
            precedence.index("Never invent a claim"),
            precedence.index("Awareness governs position"),
        )

    def test_every_rule_names_its_check(self):
        text = STANDARD.read_text(encoding="utf-8")
        sections = text.split("### ")[1:]
        creative = [section for section in sections if section[:2].rstrip(".").isdigit()]
        self.assertEqual(len(RULES), len(creative))
        for section in creative:
            with self.subTest(rule=section.splitlines()[0]):
                self.assertIn("**The check", section)

    def test_hard_rule_requires_the_standard(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        rules = skill.split("## Hard rules", 1)[1]
        self.assertIn("references/26-copywriting-standards.md", rules)

    def test_contradictions_are_resolved_rather_than_left_standing(self):
        doctrine = (ROOT / "references" / "21-evidence-and-doctrine.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("### Benefit versus mechanism", doctrine)
        self.assertIn("### Hedging: which ones to kill", doctrine)
        # The resolution has to permit mechanism as an SLA lead, because the awareness model
        # requires it. A flat reading of rule 12 would forbid it.
        self.assertIn("A mechanism may lead", doctrine)
        self.assertIn("may never appear without the payoff", doctrine)

    def test_contracts_point_at_the_lexicon(self):
        for relative in CONTRACTS_WITH_LEXICON_CHECK:
            with self.subTest(contract=relative):
                text = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("config/copy-lexicon.yml", text)


class LexiconTests(unittest.TestCase):
    def setUp(self):
        self.checker = load_checker()
        self.lexicon = self.checker.read_lexicon(LEXICON)

    def test_every_tier_parses_and_is_populated(self):
        for key in ("banned_phrases", "flagged_words", "hedge_phrases", "structural_tells"):
            with self.subTest(key=key):
                self.assertTrue(self.lexicon[key], f"{key} should not be empty")

    def test_entries_are_lowercase_and_unquoted(self):
        for key in ("banned_phrases", "flagged_words", "hedge_phrases"):
            for entry in self.lexicon[key]:
                with self.subTest(entry=entry):
                    self.assertEqual(entry, entry.lower())
                    self.assertNotIn('"', entry)
                    self.assertFalse(entry.startswith("'"))

    def test_no_tier_overlap(self):
        banned = set(self.lexicon["banned_phrases"])
        flagged = set(self.lexicon["flagged_words"])
        hedges = set(self.lexicon["hedge_phrases"])
        self.assertEqual(set(), banned & flagged)
        self.assertEqual(set(), banned & hedges)
        self.assertEqual(set(), flagged & hedges)

    def test_flagged_words_stay_out_of_the_banned_tier(self):
        # "Seamless" is a lie in a brand promise and a fact in a garment description, so it
        # must never be promoted to an outright ban. Same for the other literal-use words.
        for word in ("seamless", "robust", "transform", "harness"):
            with self.subTest(word=word):
                self.assertNotIn(word, self.lexicon["banned_phrases"])
                self.assertIn(word, self.lexicon["flagged_words"])


class CheckerBehaviourTests(unittest.TestCase):
    def setUp(self):
        self.checker = load_checker()

    def test_detects_a_banned_phrase(self):
        result = run_checker("--text", "In today's world, mornings are hard.")
        self.assertEqual(1, result.returncode, result.stdout)
        self.assertIn("BANNED", result.stdout)

    def test_matches_a_typographic_apostrophe(self):
        # Copy arrives with smart quotes from every real editor, so a straight-quote-only
        # match would miss almost every genuine violation.
        result = run_checker("--text", "In today\u2019s world, mornings are hard.")
        self.assertEqual(1, result.returncode, result.stdout)

    def test_matches_a_wildcard_template(self):
        result = run_checker("--text", "That's where Acme Greens comes in.")
        self.assertEqual(1, result.returncode, result.stdout)

    def test_hedges_are_reported_but_never_fatal(self):
        # "Helps support" is the approved structure-function wording for a supplement in
        # several markets, so failing the run on it would punish the compliant form.
        result = run_checker("--text", "Helps support healthy energy levels.")
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("hedge", result.stdout)

    def test_flagged_words_are_not_fatal_by_default_and_are_under_strict(self):
        clean = run_checker("--text", "A seamless waistband.")
        self.assertEqual(0, clean.returncode, clean.stdout)
        self.assertIn("flagged", clean.stdout)

        strict = run_checker("--strict", "--text", "A seamless waistband.")
        self.assertEqual(1, strict.returncode, strict.stdout)

    def test_clean_copy_passes(self):
        result = run_checker("--text", "Three weeks in, the 4am wake-up stopped.")
        self.assertEqual(0, result.returncode, result.stdout)

    def test_text_only_does_not_also_scan_the_examples(self):
        result = run_checker("--text", "Three weeks in, the 4am wake-up stopped.")
        self.assertIn("1 source(s)", result.stdout)

    def test_frozen_examples_carry_no_banned_phrase(self):
        # The real enforcement: examples/ are frozen representations of agent output, so a
        # tier-one phrase reaching one of them means the standard is being documented and
        # not followed.
        result = run_checker()
        self.assertNotIn("BANNED", result.stdout)
        self.assertEqual(0, result.returncode, result.stdout)

    def test_scans_every_example_file(self):
        # Guards against the default scope silently narrowing to nothing, which would make
        # the check above pass vacuously.
        result = run_checker()
        expected = len(list((ROOT / "examples").glob("*.md")))
        self.assertGreater(expected, 0)
        self.assertIn(f"{expected} source(s)", result.stdout)


class ShippedBundleTests(unittest.TestCase):
    """The upload-only install path is "download this file and paste it".

    The bundles were gitignored, so README's first instruction linked to a path that did not
    exist in a fresh clone and the paste-in install was impossible without running Python.
    They now ship, which means they can go stale, which is what these check.
    """

    BUNDLES = ("dist/craft-bundle.md", "dist/knowledge-bundle.md")
    BUILDERS = {
        "dist/craft-bundle.md": "scripts/build-craft-bundle.py",
        "dist/knowledge-bundle.md": "scripts/build-knowledge-bundle.py",
    }

    def test_bundles_are_present(self):
        for relative in self.BUNDLES:
            with self.subTest(bundle=relative):
                self.assertTrue((ROOT / relative).is_file(), f"{relative} should ship")

    def test_bundles_are_current(self):
        for relative, builder in self.BUILDERS.items():
            with self.subTest(bundle=relative):
                result = subprocess.run(
                    [sys.executable, str(ROOT / builder), "--check"],
                    capture_output=True,
                    text=True,
                    cwd=ROOT,
                )
                self.assertEqual(
                    0,
                    result.returncode,
                    f"{relative} is stale, run {builder}: {result.stderr}",
                )

    def test_bundles_are_not_gitignored(self):
        for relative in self.BUNDLES:
            with self.subTest(bundle=relative):
                result = subprocess.run(
                    ["git", "check-ignore", "-q", relative],
                    capture_output=True,
                    cwd=ROOT,
                )
                self.assertEqual(
                    1, result.returncode, f"{relative} must not be gitignored, it ships"
                )

    def test_craft_bundle_carries_the_new_standard(self):
        bundle = (ROOT / "dist" / "craft-bundle.md").read_text(encoding="utf-8")
        self.assertIn("references/26-copywriting-standards.md", bundle)
        self.assertIn("Precedence, when two of them collide", bundle)

    def test_readme_links_resolve(self):
        # The specific failure this guards: a quick-start link to a generated artefact that
        # is not in the repository.
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for relative in self.BUNDLES:
            with self.subTest(bundle=relative):
                if f"({relative})" in readme:
                    self.assertTrue((ROOT / relative).is_file())


class RubricWiringTests(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(ROOT / "evals"))
        self.addCleanup(sys.path.remove, str(ROOT / "evals"))
        import rubric

        self.rubric = rubric

    def test_new_criteria_are_scored(self):
        keys = {key for key, _ in self.rubric.CRITERIA}
        for key in (
            "end_state",
            "concision",
            "reader_selection",
            "tone_per_slot",
            "no_hedging",
            "mechanism_payoff",
            "front_loaded",
            "no_ai_lexicon",
        ):
            with self.subTest(key=key):
                self.assertIn(key, keys)

    def test_groups_cover_every_criterion_exactly_once(self):
        grouped = [key for _, keys in self.rubric.GROUPS for key in keys]
        self.assertEqual([key for key, _ in self.rubric.CRITERIA], grouped)
        self.assertEqual(len(set(grouped)), len(grouped))

    def test_groups_render_into_the_judge_prompt(self):
        prompt = self.rubric.judge_prompt("brief", "output")
        for group, _ in self.rubric.GROUPS:
            with self.subTest(group=group):
                self.assertIn(f"### {group}", prompt)

    def test_hedging_criterion_exempts_approved_wording(self):
        # Without this the judge would penalise the compliant form of a regulated claim.
        described = dict(self.rubric.CRITERIA)
        self.assertIn("approved", described["no_hedging"])

    def test_awareness_exceptions_are_stated_in_the_criteria(self):
        # end_state and front_loaded both have a UWA exception. If the criterion text loses
        # it, the eval starts penalising correct cold-traffic openings.
        described = dict(self.rubric.CRITERIA)
        self.assertIn("UWA", described["end_state"])
        self.assertIn("UWA", described["front_loaded"])


if __name__ == "__main__":
    unittest.main()
