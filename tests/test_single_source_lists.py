"""One list, one source.

Every defect found in the 1.0.0 cleanup was the same shape: a list written down in two
places with nothing forcing agreement. The worst of them cost a real measurement, because
`evals/run.py` kept a twelve-file craft stack while `SKILL.md` had grown to fifteen, so the
eval scored an agent that had never read `references/26-copywriting-standards.md` against
eight criteria drawn from it.

The pattern that never drifted was `scripts/build-craft-bundle.py`, which parses its list out
of `SKILL.md` instead of restating it. This module holds every place that pattern is now
applied, plus a pin on the lists that are prose and cannot be derived.

Adding a list that exists twice without a test here is how the defect comes back.
"""

import importlib.util
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
STANDARD = ROOT / "references" / "26-copywriting-standards.md"


def load(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def builder():
    return load("build_craft_bundle", ROOT / "scripts" / "build-craft-bundle.py")


def rubric():
    sys.path.insert(0, str(ROOT / "evals"))
    try:
        import rubric as module
    finally:
        sys.path.remove(str(ROOT / "evals"))
    return module


class CraftStackTests(unittest.TestCase):
    """The list whose drift cost the 35.25/36 reading."""

    def test_the_eval_and_the_bundle_agree_with_the_skill(self):
        run = load("evals_run", ROOT / "evals" / "run.py")
        declared = tuple(builder().craft_stack())

        self.assertEqual(declared, tuple(run.CRAFT_STACK))
        self.assertGreaterEqual(len(declared), 15)

    def test_every_declared_reference_exists(self):
        for relative in builder().craft_stack():
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())

    def test_neither_consumer_hardcodes_a_reference_list(self):
        # The specific regression: a module-level tuple of reference paths. If one reappears,
        # the two consumers can disagree with SKILL.md again without any test noticing.
        for relative in ("evals/run.py", "scripts/build-craft-bundle.py"):
            with self.subTest(source=relative):
                text = (ROOT / relative).read_text(encoding="utf-8")
                literals = re.findall(r'^\s+"references/[^"]+\.md",\s*$', text, re.MULTILINE)
                self.assertEqual([], literals, f"{relative} lists references literally again")


class ContractListTests(unittest.TestCase):
    """The craft bundle shipped seven contracts while the skill offered thirteen."""

    def test_every_offered_contract_is_bundled_or_deliberately_excluded(self):
        module = builder()
        offered = set(
            re.findall(
                r"`(contracts/[^`]+\.md)`",
                module.section_after(module.FORMATS_SECTION, "###"),
            )
        )
        classified = set(module.contracts()) | set(module.CHAT_SURFACE_EXCLUSIONS)

        self.assertEqual(offered, classified)
        self.assertGreaterEqual(len(offered), 13)

    def test_every_exclusion_states_a_reason(self):
        for relative, reason in builder().CHAT_SURFACE_EXCLUSIONS.items():
            with self.subTest(contract=relative):
                self.assertGreater(len(reason), 20, "an exclusion without a reason is a guess")

    def test_every_classified_contract_exists(self):
        module = builder()
        for relative in list(module.contracts()) + list(module.CHAT_SURFACE_EXCLUSIONS):
            with self.subTest(contract=relative):
                self.assertTrue((ROOT / relative).is_file())


class LexiconTests(unittest.TestCase):
    """The rubric restated eight of the tier-one phrases inside a criterion description."""

    def test_the_rubric_derives_the_banned_list_from_the_lexicon(self):
        lexicon = load("copy_lexicon_probe", ROOT / "scripts" / "copy_lexicon.py").read_lexicon()
        described = dict(rubric().CRITERIA)["no_ai_lexicon"]

        self.assertGreaterEqual(len(lexicon["banned_phrases"]), 20)
        for phrase in lexicon["banned_phrases"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.replace("*", "X"), described)

    def test_the_checker_and_the_rubric_read_one_parser(self):
        # Two copies of the reader would drift the same way two copies of the list would.
        for relative in ("scripts/check-copy-lexicon.py", "evals/rubric.py"):
            with self.subTest(source=relative):
                text = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("copy_lexicon", text)
                self.assertNotIn("def read_lexicon", text)


class RubricProseTests(unittest.TestCase):
    """Criterion names appear in prose in two files. Prose cannot derive, so it is pinned."""

    def test_the_standard_only_claims_criteria_that_exist(self):
        keys = {key for key, _ in rubric().CRITERIA}
        claimed = set(re.findall(r"`([a-z_]+)` in the eval", STANDARD.read_text(encoding="utf-8")))

        self.assertGreaterEqual(len(claimed), 8)
        self.assertEqual(set(), claimed - keys, "the standard cites eval criteria that do not exist")

    def readme_criterion_rows(self):
        """The left-hand cell of every criterion row in the README's three tables."""
        readme = (ROOT / "evals" / "README.md").read_text(encoding="utf-8")
        rows = []
        for line in readme.splitlines():
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) != 2 or not cells[0] or set(cells[0]) <= {"-"}:
                continue
            if cells[0] == "Criterion":
                continue
            rows.append(cells[0])
        return rows

    def test_the_eval_readme_documents_every_criterion_and_nothing_else(self):
        # Row count as well as membership, so a criterion added to the rubric and forgotten in
        # the README fails here rather than quietly going undocumented.
        keys = [key for key, _ in rubric().CRITERIA]
        rows = self.readme_criterion_rows()

        self.assertEqual(len(keys), len(rows), f"README documents {len(rows)} of {len(keys)}")
        normalised = {re.sub(r"[^a-z]", "", row.lower()) for row in rows}
        for key in keys:
            with self.subTest(key=key):
                self.assertIn(re.sub(r"[^a-z]", "", key), normalised)

    def test_the_readme_states_the_current_maximum(self):
        readme = (ROOT / "evals" / "README.md").read_text(encoding="utf-8")

        self.assertIn(str(rubric().MAX_SCORE), readme)


class PrecedenceTests(unittest.TestCase):
    """Which source is canonical is itself a fact that was written down in six places.

    1.0.0 moved canonical status from the Notion hub to this repository and left the old claim
    standing in the README, two connector files and `references/20-hook-quality-standard.md`.
    The last one is the reason this is a test rather than a one-time edit: it is an always-loaded
    craft file, and it survived a line-based search because the sentence wrapped across two lines
    with "hub is" ending one and "canonical" starting the next.
    """

    # docs/notion-archive/ records the migration and has to describe the retired rule to explain
    # it. Everywhere else, asserting it is a defect.
    ALLOWED = ("docs/notion-archive/", "dist/")
    STALE = re.compile(r"Notion[\s\S]{0,120}?\bis canonical", re.IGNORECASE)

    def sources(self):
        for path in sorted(ROOT.rglob("*.md")):
            relative = path.relative_to(ROOT).as_posix()
            if relative.startswith(self.ALLOWED) or ".git" in path.parts:
                continue
            yield relative, path.read_text(encoding="utf-8")

    def test_nothing_still_claims_notion_is_canonical(self):
        offenders = []
        for relative, text in self.sources():
            for match in self.STALE.finditer(text):
                # The corrected sentences say the repository is canonical and mention Notion in
                # the same breath, which is the wording that replaced the defect.
                window = match.group(0)
                if re.search(r"repository is canonical", window, re.IGNORECASE):
                    continue
                offenders.append(f"{relative}: {' '.join(window.split())}")

        self.assertEqual([], offenders)

    def test_the_one_file_that_declares_precedence_says_the_repository(self):
        text = STANDARD.parent.joinpath("18-master-creative-strategy.md").read_text(encoding="utf-8")

        self.assertIn("This repository is canonical for the universal method", text)
        self.assertIn("Conversation memory is never canonical", text)


class GeneratedFileTests(unittest.TestCase):
    """AGENTS.md is SKILL.md rendered, so its lists must never be edited in place."""

    def test_agents_md_declares_itself_generated(self):
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")

        for heading in ("The craft stack, always loaded", "Launch invariants", "Hard rules"):
            with self.subTest(heading=heading):
                self.assertIn(heading, text)
                self.assertIn(heading, skill)


if __name__ == "__main__":
    unittest.main()
