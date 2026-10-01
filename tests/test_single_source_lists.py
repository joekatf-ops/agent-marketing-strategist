"""One list, one source.

Every defect found in the 1.0.0 cleanup was the same shape: a list written down in two
places with nothing forcing agreement. This module pins the lists that are prose and cannot
be derived. The craft-stack, contract, lexicon and rubric lists it used to pin left the
package in 1.9.0 with the copy method; ad copy now follows the DTC Ad Copywriting playbook.

Adding a list that exists twice without a test here is how the defect comes back.
"""

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
REFERENCES = ROOT / "references"


class PrecedenceTests(unittest.TestCase):
    """Which source is canonical is itself a fact that was written down in six places.

    1.0.0 moved canonical status from the Notion hub to this repository and left the old claim
    standing in the README, two connector files and an always-loaded craft file. The last one is
    the reason this is a test rather than a one-time edit: it survived a line-based search because
    the sentence wrapped across two lines with "hub is" ending one and "canonical" starting the
    next.
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
        text = REFERENCES.joinpath("18-master-creative-strategy.md").read_text(encoding="utf-8")

        self.assertIn("This repository is canonical for the universal method", text)
        self.assertIn("Conversation memory is never canonical", text)


class NotionArchiveTests(unittest.TestCase):
    """`MANIFEST.md` is the archive's index, so it and the directory must not disagree.

    The archive stopped being a verbatim export on 1 September 2026, when the page built around a
    real client brand was removed and four brand-name mentions were redacted. That is defensible
    only while the archive says so: a redacted record that declares its redactions is trustworthy,
    and one that quietly differs from its own index is not. This is the pin.
    """

    ARCHIVE = ROOT / "docs" / "notion-archive"
    ROW = re.compile(r"^\|\s*(?P<file>[^|]+?)\s*\|\s*(?P<page_id>[0-9a-f]{32})\s*\|", re.MULTILINE)

    def manifest_rows(self):
        text = (self.ARCHIVE / "MANIFEST.md").read_text(encoding="utf-8")
        rows = [match.group("file") for match in self.ROW.finditer(text)]
        self.assertTrue(rows, "the manifest table did not parse, so nothing below is meaningful")
        return rows

    def test_every_manifest_row_names_a_present_file_or_says_it_was_removed(self):
        missing = [
            row
            for row in self.manifest_rows()
            if not row.startswith("removed") and not (self.ARCHIVE / row).is_file()
        ]

        self.assertEqual([], missing, "manifest rows pointing at files that are not there")

    def test_every_archived_page_appears_in_the_manifest(self):
        listed = set(self.manifest_rows())
        present = {
            path.name
            for path in self.ARCHIVE.glob("*.md")
            if path.name not in {"README.md", "MANIFEST.md"}
        }

        self.assertEqual(set(), present - listed, "archived pages absent from the manifest")

    def test_the_redaction_is_declared_rather_than_silent(self):
        readme = (self.ARCHIVE / "README.md").read_text(encoding="utf-8")

        self.assertIn("What was redacted", readme)
        # The removed page's row is kept for traceability, so the count stays twelve while the
        # files on disk are eleven. Both numbers have to survive together or the record lies.
        self.assertEqual(12, len(self.manifest_rows()))
        self.assertEqual(11, len(list(self.ARCHIVE.glob("*.md"))) - 2)


class GeneratedFileTests(unittest.TestCase):
    """AGENTS.md is SKILL.md rendered, so its lists must never be edited in place."""

    def test_agents_md_declares_itself_generated(self):
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")

        for heading in ("Core reference", "Launch invariants", "Hard rules"):
            with self.subTest(heading=heading):
                self.assertIn(heading, text)
                self.assertIn(heading, skill)


if __name__ == "__main__":
    unittest.main()
