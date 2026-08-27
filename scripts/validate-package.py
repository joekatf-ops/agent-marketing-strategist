#!/usr/bin/env python3
"""Validate routing, frozen examples and duplicated entrypoints."""

from __future__ import annotations

import ast
import collections
import importlib.util
import pathlib
import re
import sysconfig
import sys


ROUTED_PATH = re.compile(
    r"`((?:references|contracts|examples|connectors|schemas)/[^`]+\.(?:md|json))`"
)
PLACEHOLDER = re.compile(r"\{\{[^}]+\}\}|\b(?:TODO|TBD)\b")
SUPERSEDED_CONCEPT_MODEL = re.compile(r"persona\s+x\s+outcome\s+x\s+angle", re.IGNORECASE)
STANDARD_AD_CONTRACTS = (
    "contracts/ad-copy.md",
    "contracts/hook-batch.md",
    "contracts/video-script.md",
    "contracts/static-spec.md",
)
MOST_AWARE_ROW = re.compile(
    r"^[ \t]*\|[ \t]*(?:MWA|MOST[ \t]+AWARE)[ \t]*\|",
    re.IGNORECASE | re.MULTILINE,
)
TEMPLATE_TEST_REGISTER = "templates/brand-folder/strategy/test-register.yml"
CONTST_TEST_ID = re.compile(
    r"^[ \t-]*test_id:[ \t]*(CONTST(?P<number>\d{3}))[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
V03_REQUIRED_FILES = (
    "references/18-master-creative-strategy.md",
    "contracts/campaign-launch-plan.md",
    "contracts/destination-handoff.md",
    "examples/campaign-launch-plan.md",
    "examples/destination-handoff.md",
    "connectors/notion-composio.md",
)
V04_REQUIRED_FILES = (
    "contracts/brand-readiness.md",
    "contracts/customer-intelligence.md",
    "contracts/concept-batch.md",
    "contracts/hook-batch.md",
    "contracts/ad-copy.md",
    "contracts/video-script.md",
    "contracts/static-spec.md",
    "contracts/learning-update.md",
    "contracts/campaign-launch-plan.md",
    "contracts/destination-handoff.md",
    "contracts/ad-diagnosis.md",
    "contracts/creative-audit.md",
    "references/19-ad-analysis-harness.md",
    "schemas/ad-analysis-intake.schema.json",
    "examples/ad-analysis-intake.json",
    "examples/creative-audit.md",
    "examples/ad-diagnosis.md",
)
CREATIVE_AUDIT_PERFORMANCE_PREDICTION = re.compile(
    r"\b(?:predict(?:s|ed|ing)?|forecast(?:s|ed|ing)?|will|would|should|"
    r"could|may|might|can|expected\s+to|likely(?:\s+to)?|guarantee(?:s|d)?)\b"
    r"[^.!?\n]*\b(?:win(?:s|ner|ning)?|convert(?:s|ed|ing)?|conversion|CAC|"
    r"scal(?:e|es|ed|ing)|outperform(?:s|ed|ing)?)\b",
    re.IGNORECASE,
)
PREDICATE_PREFIX_NEGATION = re.compile(
    r"\b(?:cannot|can't|never|(?:do|does|did|is|are|was|were|will|would|"
    r"should|could|may|might|must)\s+not)\s*$",
    re.IGNORECASE,
)
PREDICATE_INTERNAL_NEGATION = re.compile(
    r"^(?:can|could|will|would|should|may|might|must|is|are|was|were)\s+not\b",
    re.IGNORECASE,
)
NO_PREDICTION_PREFIX = re.compile(
    r"\b(?:makes?|provides?|issues?|contains?)\s+no\s+"
    r"(?:performance\s+)?(?:prediction|forecast)\b[^.!?\n]*$",
    re.IGNORECASE,
)
NO_NOMINAL_POLICY_PREFIX = re.compile(
    r"\bno(?:\s+creative\s+audit)?\s*$",
    re.IGNORECASE,
)
NEGATED_ACTION_OBJECT = re.compile(
    r"\b(?:assign(?:s|ed|ing)?|recommend(?:s|ed|ing)?|select(?:s|ed|ing)?|"
    r"use(?:s|d|ing)?|set(?:s|ting)?)\s+no\s+"
    r"`?(?:keep|ITR|stop|scale)`?\b",
    re.IGNORECASE,
)
COORDINATING_POLICY_BOUNDARY = re.compile(
    r"\s+\b(?:and|or)\b\s+(?=(?:can(?:not)?|can't|could|will|would|should|"
    r"may|might|must|do|does|did|is|are|was|were|assign|recommend|select|use|set)\b)",
    re.IGNORECASE,
)
PROHIBITIVE_POLICY_PREFIX = re.compile(
    r"\b(?:prohibit(?:s|ed|ing)?|forbid(?:s|den|ding)?|"
    r"disallow(?:s|ed|ing)?)\b[^.!?\n]*$",
    re.IGNORECASE,
)
OPTIONAL_PERFORMANCE_DECISION = re.compile(
    r"performance\s+data\s+is\s+optional\s+for\s+a\s+"
    r"keep,\s*ITR,\s*stop\s+or\s+scale\s+decision",
    re.IGNORECASE,
)
AUTOMATIC_CONTST_RESERVATION = re.compile(
    r"diagnosis\s+automatically\s+reserves\s+the\s+next\s+CONTST",
    re.IGNORECASE,
)
PERFORMANCE_ACTIONS = frozenset({"keep", "itr", "stop", "scale"})
NETWORK_DEPENDENCIES = frozenset(
    {
        "ftplib",
        "http",
        "imaplib",
        "nntplib",
        "poplib",
        "requests",
        "smtplib",
        "socket",
        "subprocess",
        "telnetlib",
        "urllib",
        "webbrowser",
        "xmlrpc",
    }
)
DIAGNOSIS_ACTION_POLICY = re.compile(
    r"`Top-level\s+action`\s+contains\s+exactly\s+one\s+literal\s+value:\s*([^\n.]+)",
    re.IGNORECASE,
)
CAMPAIGN_LAUNCH_CONTRACT = "contracts/campaign-launch-plan.md"
CREATIVE_TESTING_RULES = (
    (
        re.compile(r"^[ \t]*-[ \t]*Budget type:[ \t]*ABO\.[ \t]*$", re.MULTILINE),
        "contracts/campaign-launch-plan.md must require ABO creative testing",
    ),
    (
        re.compile(
            r"^[ \t]*-[ \t]*Absolute floor:[ \t]*\$50 per ad set per day\.[ \t]*$",
            re.MULTILINE,
        ),
        "contracts/campaign-launch-plan.md must set an absolute $50 per-ad-set daily floor",
    ),
    (
        re.compile(
            r"^[ \t]*-[ \t]*Preferred starting point:[ \t]*approximately \$100 per ad set per day\.[ \t]*$",
            re.MULTILINE,
        ),
        "contracts/campaign-launch-plan.md must make approximately $100 the preferred per-ad-set daily starting point",
    ),
    (
        re.compile(
            r"^[ \t]*-[ \t]*Planned observation window:[ \t]*five full days\.[ \t]*$",
            re.MULTILINE,
        ),
        "contracts/campaign-launch-plan.md must set a five-full-day planned observation window",
    ),
)
SCALING_RULES = (
    (
        re.compile(r"^[ \t]*-[ \t]*Budget type:[ \t]*CBO\.[ \t]*$", re.MULTILINE),
        "contracts/campaign-launch-plan.md must require CBO scaling",
    ),
    (
        re.compile(
            r"^[ \t]*-[ \t]*Graduated ads keep their real Post ID\.[ \t]*$",
            re.MULTILINE,
        ),
        "contracts/campaign-launch-plan.md must preserve graduated ads' real Post ID",
    ),
)
ENTRYPOINT_ROUTE_RULES = (
    (
        re.compile(
            r"manual\s+Meta\s+launch\s+asks.*contracts/campaign-launch-plan\.md.*"
            r"references/09-testing-and-diagnosis\.md.*destination\s+asks.*"
            r"contracts/destination-handoff\.md",
            re.IGNORECASE | re.DOTALL,
        ),
        "must route manual launch and destination asks to their governed contracts",
    ),
    (
        re.compile(
            r"no\s+adequate\s+performance\s+data\s*->\s*Creative\s+Audit",
            re.IGNORECASE,
        ),
        "must route absent or inadequate performance data to Creative Audit",
    ),
    (
        re.compile(
            r"(?<!no\s)adequate\s+performance\s+data\s*->\s*Ad\s+Diagnosis",
            re.IGNORECASE,
        ),
        "must route adequate performance data to Ad Diagnosis",
    ),
    (
        re.compile(
            r"competitor\s+ad\s*->\s*competitor\s+research",
            re.IGNORECASE,
        ),
        "must route competitor ads to competitor research",
    ),
    (
        re.compile(
            r"human\s+edit\s*->\s*Learning\s+Update",
            re.IGNORECASE,
        ),
        "must route human edits to Learning Update",
    ),
    (
        re.compile(
            r"combined\s+adequate\s+creative\s+and\s+performance\s+produces\s+"
            r"one\s+Ad\s+Diagnosis",
            re.IGNORECASE,
        ),
        "must produce one Ad Diagnosis for combined adequate creative and performance",
    ),
    (
        re.compile(
            r"(?:consume|produce|produces|write|writes)[^.!?\n]*input\s+audit"
            r"[^.!?\n]*before\s+(?:conclusions|performance\s+conclusions)",
            re.IGNORECASE,
        ),
        "must require the input audit before conclusions",
    ),
)
AD_ANALYSIS_ROUTING_CONTRADICTIONS = (
    re.compile(
        r"(?<!no\s)adequate\s+performance\s+data\s*->\s*Creative\s+Audit",
        re.IGNORECASE,
    ),
    re.compile(
        r"combined\s+adequate\s+creative\s+and\s+performance[^.!?\n]*"
        r"(?:both|two)[^.!?\n]*Creative\s+Audit[^.!?\n]*Ad\s+Diagnosis",
        re.IGNORECASE,
    ),
    re.compile(
        r"\badequate\s+performance\s+data\b[^.!?\n]*\b"
        r"(?:route(?:s|d|ing)?|use(?:s|d|ing)?|select(?:s|ed|ing)?)\b"
        r"[^.!?\n]*\bCreative\s+Audit\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"combined\s+adequate\s+creative\s+and\s+performance[^.!?\n]*"
        r"(?:both|two)[^.!?\n]*reports?[^.!?\n]*"
        r"(?:Ad\s+Diagnosis[^.!?\n]*Creative\s+Audit|"
        r"Creative\s+Audit[^.!?\n]*Ad\s+Diagnosis)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:bypass|skip|omit)(?:es|ped|ping|ted|ting)?\b[^.!?\n]*"
        r"input\s+audit|input\s+audit[^.!?\n]*\b(?:optional|unnecessary|not\s+required)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bincomplete\s+performance\b[^.!?\n]*\bconclusions?\b"
        r"[^.!?\n]*\bbefore\b[^.!?\n]*\binput\s+audit\b",
        re.IGNORECASE,
    ),
)
ENTRYPOINT_LAUNCH_RULES = (
    (
        re.compile(
            r"creative\s+testing\s+uses\s+one\s+CT\s+campaign\s+per\s+product\s+and\s+region,\s*"
            r"ABO,\s*and\s+exactly\s+one\s+CONTST\s+batch\s+per\s+ad\s+set",
            re.IGNORECASE,
        ),
        "must require CT/ABO with one CONTST batch per ad set",
    ),
    (
        re.compile(
            r"initial\s+NNT\s+or\s+INSPO\s+batch\s+contains\s+exactly\s+four\s+ads:\s*"
            r"UWA,\s*PRA,\s*SLA\s+and\s+PDA",
            re.IGNORECASE,
        ),
        "must lock the four initial NNT/INSPO ads",
    ),
    (
        re.compile(
            r"daily\s+ad-set\s+budget\s+has\s+an\s+absolute\s+\$50\s+floor\s+and\s+an\s+"
            r"approximately\s+\$100\s+preferred\s+starting\s+point",
            re.IGNORECASE,
        ),
        "must preserve the $50 floor and approximately $100 preferred budget",
    ),
    (
        re.compile(
            r"five\s+full\s+days\s+of\s+observation.*five-day\s+read\s+is\s+still\s+"
            r"directional\s+or\s+too\s+early\s+unless\s+every\s+active\s+validity\s+threshold\s+is\s+met",
            re.IGNORECASE | re.DOTALL,
        ),
        "must preserve five full days and the validity caveat",
    ),
    (
        re.compile(
            r"scaling\s+uses\s+a\s+separate\s+SC\s+campaign\s+with\s+CBO,\s*and\s+"
            r"graduated\s+ads\s+retain\s+their\s+real\s+Post\s+IDs",
            re.IGNORECASE,
        ),
        "must require SC/CBO scaling with real Post IDs",
    ),
    (
        re.compile(
            re.escape("[BRAND]_[PRODUCT]_[CT|SC]_[ABO|CBO]_[REGION]_[YYYYMMDD]")
        ),
        "must preserve the campaign naming shape",
    ),
    (
        re.compile(re.escape("[CONTST###]_[NNT|INSPO|ITR]_[WHO]_[PROBLEM]")),
        "must preserve the ad-set naming shape",
    ),
    (
        re.compile(
            re.escape(
                "[FULL_AD_SET_NAME]_[UWA|PRA|SLA|PDA]_[FORMAT]_[LP|PDP|HP|CP]_[POSTID]"
            )
        ),
        "must preserve the full ad naming shape",
    ),
    (
        re.compile(
            r"UWA\s+and\s+PRA\s+default\s+to\s+LP;\s*SLA\s+and\s+PDA\s+default\s+to\s+PDP.*"
            r"exception\s+maps\s+to\s+LP,\s*PDP,\s*HP\s+or\s+CP\s+through\s+a\s+Destination\s+Handoff",
            re.IGNORECASE | re.DOTALL,
        ),
        "must preserve destination defaults and controlled exceptions",
    ),
    (
        re.compile(
            r"new\s+ad\s+name\s+ends\s+in\s+`?POSTIDXXX`?.*preserve\s+the\s+real\s+Post\s+ID",
            re.IGNORECASE | re.DOTALL,
        ),
        "must end new ad names in POSTIDXXX and preserve published Post IDs",
    ),
    (
        re.compile(
            r"Launch\s+plans\s+and\s+changes\s+are\s+manual\s+only.*Never\s+publish\s+ads\s+or\s+"
            r"change\s+budgets\s+automatically",
            re.IGNORECASE | re.DOTALL,
        ),
        "must keep launch and budget changes manual only",
    ),
    (
        re.compile(
            r"Generic\s+count\s+overrides\s+cannot\s+change\s+the\s+locked\s+four\s+initial\s+"
            r"NNT\s+or\s+INSPO\s+ads\s+or\s+one\s+selected\s+hook\s+per\s+launch\s+ad.*"
            r"human-reviewed\s+universal-method\s+change",
            re.IGNORECASE | re.DOTALL,
        ),
        "must protect locked initial-ad and selected-hook counts",
    ),
)
LEGACY_PLATFORM_POLICIES = (
    (
        re.compile(r"default\s+duration\s+(?:is\s+)?7\s+days", re.IGNORECASE),
        "legacy seven-day test default",
    ),
    (
        re.compile(
            r"current\s+standard\s+shape[^\n]*10\s+concepts\s+x\s+5\s+to\s+10\s+hook\s+variations|"
            r"hook[^\n]*actual\s+test\s+variable|under\s+roughly\s+\$30k/month\s+use",
            re.IGNORECASE,
        ),
        "legacy volume-first hook test standard",
    ),
)
READ_VALIDITY_RULES = (
    re.compile(
        r"1\.\s+\*\*Too early\.\*\*.*fewer than five full days.*regardless of spend or "
        r"purchases.*five or more full days.*neither.*spend.*nor.*purchase",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"2\.\s+\*\*Verdict\.\*\*.*five or more full days.*all.*spend.*purchase.*"
        r"no material integrity failure.*no uneven delivery.*no logged intervention",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"3\.\s+\*\*Direction\.\*\*.*remaining.*five-or-more-day.*at least one.*"
        r"spend.*purchase.*not all.*all thresholds.*uneven\s+delivery.*logged\s+intervention",
        re.IGNORECASE | re.DOTALL,
    ),
)


def operating_body(text: str) -> str:
    if text.startswith("---\n"):
        closing = text.find("\n---\n", 4)
        if closing != -1:
            text = text[closing + 5 :]
    heading = text.find("# Marketing Strategist")
    if heading != -1:
        text = text[heading:]
    return text.strip()


def markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"^##[ \t]+{re.escape(heading)}[ \t]*$", text, re.IGNORECASE | re.MULTILINE
    )
    if match is None:
        return ""
    next_heading = re.search(r"^##[ \t]+", text[match.end() :], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[match.end() : end]


def classify_read_validity(
    full_days: int,
    spend_thresholds_met: bool,
    purchase_thresholds_met: bool,
    material_integrity_failure: bool,
    uneven_delivery: bool,
    logged_intervention: bool,
) -> str:
    if full_days < 5:
        return "Too early"
    if not spend_thresholds_met and not purchase_thresholds_met:
        return "Too early"
    if (
        spend_thresholds_met
        and purchase_thresholds_met
        and not material_integrity_failure
        and not uneven_delivery
        and not logged_intervention
    ):
        return "Verdict"
    return "Direction"


def policy_clauses(text: str) -> list[str]:
    return re.split(
        r"(?<=[.!?])\s+|\n+|[,;](?=\s)|[—–]|\s+-{1,2}\s+|"
        r"\s+(?=\(\s*not\b)|\s+\b(?:but|although|however)\b\s+",
        text,
        flags=re.IGNORECASE,
    )


def is_negated_policy_clause(clause: str) -> bool:
    return bool(
        re.search(
            r"\b(?:not|never|no|without|exclude(?:d|s)?|prohibit(?:ed|s)?|"
            r"forbid(?:den|s)?|disallow(?:ed|s)?|cannot|can't|isn't|aren't|do\s+not)\b",
            clause,
            re.IGNORECASE,
        )
    )


def policy_predicates(text: str) -> list[str]:
    predicates: list[str] = []
    for clause in policy_clauses(text):
        parts = COORDINATING_POLICY_BOUNDARY.split(clause)
        subject = "Creative Audit" if "creative audit" in clause.lower() else ""
        for index, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            if index and subject and "creative audit" not in part.lower():
                part = f"{subject} {part}"
            predicates.append(part)
    return predicates


def is_policy_match_negated(
    predicate: str,
    match: re.Match[str],
    target: re.Match[str] | None = None,
) -> bool:
    prefix = predicate[: match.start()]
    matched_text = match.group(0)
    if PREDICATE_PREFIX_NEGATION.search(prefix):
        return True
    if PREDICATE_INTERNAL_NEGATION.search(matched_text):
        return True
    if NO_PREDICTION_PREFIX.search(prefix):
        return True
    if NO_NOMINAL_POLICY_PREFIX.search(prefix):
        return True
    if target is not None and NEGATED_ACTION_OBJECT.search(
        predicate[match.start() : target.end()]
    ):
        return True
    return bool(PROHIBITIVE_POLICY_PREFIX.search(prefix))


def normalized_ad_analysis_routing(text: str) -> str:
    section = markdown_section(text, "Ad-analysis routing")
    normalized = re.sub(r"\s+", " ", section).strip().lower()
    return normalized.replace("for ad analysis in upload mode", "in upload mode")


def contradicts_ad_analysis_routing(text: str) -> bool:
    return any(pattern.search(text) for pattern in AD_ANALYSIS_ROUTING_CONTRADICTIONS)


def prescribes_most_aware_standard_ad(text: str) -> bool:
    for clause in policy_clauses(text):
        if not re.search(r"\b(?:Most\s+Aware|MWA)\b", clause, re.IGNORECASE):
            continue
        if not re.search(r"\bstandard[- ]ad\b", clause, re.IGNORECASE):
            continue
        if is_negated_policy_clause(clause):
            continue
        if re.search(
            r"\b(?:is|are|as|becomes?|serves?|counts?|remains?|include|includes|included|"
            r"require|requires|required|create|creates|created|build|builds|built|add|adds|"
            r"added|use|uses|used|treat|treats|treated|make|makes|made|must|should)\b",
            clause,
            re.IGNORECASE,
        ):
            return True
    return False


def contradicts_initial_ad_count(text: str) -> bool:
    for clause in policy_clauses(text):
        if is_negated_policy_clause(clause):
            continue
        if (
            re.search(r"\binitial\b", clause, re.IGNORECASE)
            and re.search(r"\b(?:NNT|INSPO)\b", clause, re.IGNORECASE)
            and re.search(r"\b(?:5|five)\b", clause, re.IGNORECASE)
            and re.search(r"\bads?\b", clause, re.IGNORECASE)
        ):
            return True
    return False


def permits_automatic_meta_change(text: str) -> bool:
    for clause in policy_clauses(text):
        if is_negated_policy_clause(clause):
            continue
        automatic = re.search(
            r"\b(?:auto(?:matic(?:ally|ed)?)?|automated)\b", clause, re.IGNORECASE
        ) or re.search(r"\bauto-(?:publish|change|adjust)", clause, re.IGNORECASE)
        action = re.search(
            r"\b(?:publish(?:ed|es|ing)?|budget(?:s)?|change(?:d|s|ing)?|"
            r"adjust(?:ed|s|ing)?)\b",
            clause,
            re.IGNORECASE,
        )
        if automatic and action:
            return True
    return False


def permits_pre_five_day_verdict(text: str) -> bool:
    pre_five = re.compile(
        r"\b(?:day[- ]?(?:1|2|3|4|one|two|three|four)|"
        r"(?:1|2|3|4|one|two|three|four)[- ]days?|"
        r"before\s+(?:day\s+)?(?:5|five)|fewer\s+than\s+(?:5|five)\s+full\s+days|"
        r"under\s+(?:5|five)\s+full\s+days)\b",
        re.IGNORECASE,
    )
    for clause in policy_clauses(text):
        if is_negated_policy_clause(clause):
            continue
        if (
            re.search(r"\bVerdict\b", clause, re.IGNORECASE)
            and pre_five.search(clause)
            and re.search(
                r"\b(?:permit(?:s|ted)?|allow(?:s|ed)?|qualif(?:y|ies|ied)|"
                r"can|may|is|becomes?)\b",
                clause,
                re.IGNORECASE,
            )
        ):
            return True
    return False


def sets_seven_day_test_default(text: str) -> bool:
    for clause in policy_clauses(text):
        if is_negated_policy_clause(clause):
            continue
        if (
            re.search(r"\b(?:7|seven)[- ]days?\b", clause, re.IGNORECASE)
            and re.search(r"\btest\s+duration\b", clause, re.IGNORECASE)
            and re.search(r"\b(?:default|standard|use|set)\b", clause, re.IGNORECASE)
            and not re.search(
                r"\b(?:external|benchmark|observation|reported?|source|Flighted|Kruse)\b",
                clause,
                re.IGNORECASE,
            )
        ):
            return True
    return False


def active_instruction_paths(root: pathlib.Path) -> list[pathlib.Path]:
    paths = [
        root / relative
        for relative in ("SKILL.md", "AGENTS.md", "PROMPT.md", "OUTPUT-CONTRACT.md")
    ]
    for folder in ("references", "contracts"):
        directory = root / folder
        if directory.is_dir():
            paths.extend(sorted(directory.glob("*.md")))
    return [path for path in paths if path.is_file()]


def creative_audit_assigns_performance_action(text: str) -> bool:
    trigger_pattern = re.compile(
        r"\b(?:action|outcome|decision|recommendation|assign(?:s|ed|ing)?|"
        r"recommend(?:s|ed|ing)?|select(?:s|ed|ing)?|use(?:s|d|ing)?|"
        r"set(?:s|ting)?)\b",
        re.IGNORECASE,
    )
    action_pattern = re.compile(r"\b(?:keep|ITR|stop|scale)\b", re.IGNORECASE)
    for predicate in policy_predicates(text):
        lowered = predicate.lower()
        action = action_pattern.search(predicate)
        if action is None:
            continue
        triggers = [
            match
            for match in trigger_pattern.finditer(predicate)
            if match.start() < action.start()
        ]
        trigger = triggers[-1] if triggers else None
        if trigger is None or (
            "creative audit" not in lowered
            and trigger.group(0).lower()
            not in {"action", "outcome", "decision", "recommendation"}
        ):
            continue
        if not is_policy_match_negated(predicate, trigger, action):
            return True
    return False


def creative_audit_predicts_performance(text: str) -> bool:
    for predicate in policy_predicates(text):
        prediction = CREATIVE_AUDIT_PERFORMANCE_PREDICTION.search(predicate)
        if prediction is not None and not is_policy_match_negated(
            predicate, prediction
        ):
            return True
    return False


def diagnosis_actions_are_governed(text: str) -> bool:
    policies = DIAGNOSIS_ACTION_POLICY.findall(text)
    if not policies:
        return False
    for policy in policies:
        actions = {
            action.lower()
            for action in re.findall(r"`([^`]+)`", policy)
        }
        if actions != PERFORMANCE_ACTIONS:
            return False
    return True


def harness_imports_are_safe(path: pathlib.Path) -> list[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    standard_library = pathlib.Path(sysconfig.get_paths()["stdlib"]).resolve()
    unsafe: list[str] = []
    for name in sorted(imports - {"__future__"}):
        if name in NETWORK_DEPENDENCIES:
            unsafe.append(name)
            continue
        spec = importlib.util.find_spec(name)
        if spec is None or spec.origin not in {"built-in", "frozen"}:
            try:
                origin = pathlib.Path(spec.origin).resolve()
                origin.relative_to(standard_library)
            except (AttributeError, TypeError, ValueError):
                unsafe.append(name)
                continue
            if "site-packages" in origin.parts:
                unsafe.append(name)
    return unsafe


def validate(root: pathlib.Path) -> list[str]:
    errors: list[str] = []
    required = ("SKILL.md", "AGENTS.md", "PROMPT.md", "VERSION")
    for relative in required:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    skill_path = root / "SKILL.md"
    agents_path = root / "AGENTS.md"
    if skill_path.is_file():
        skill_text = skill_path.read_text()
        for relative in sorted(set(ROUTED_PATH.findall(skill_text))):
            if not (root / relative).is_file():
                errors.append(f"SKILL.md references missing path: {relative}")
    else:
        skill_text = ""

    analysis_routing_sections: dict[str, str] = {}
    for relative in ("SKILL.md", "AGENTS.md", "PROMPT.md"):
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text()
        analysis_routing_sections[relative] = normalized_ad_analysis_routing(text)
        if SUPERSEDED_CONCEPT_MODEL.search(text):
            errors.append(f"{relative} contains superseded concept model")
        for pattern, error in ENTRYPOINT_ROUTE_RULES:
            if not pattern.search(text):
                errors.append(f"{relative} {error}")
        if contradicts_ad_analysis_routing(text):
            errors.append(f"{relative} contains contradictory ad-analysis routing")
        launch_invariants = markdown_section(text, "Launch invariants")
        for pattern, error in ENTRYPOINT_LAUNCH_RULES:
            if not pattern.search(launch_invariants):
                errors.append(f"{relative} {error}")
        if contradicts_initial_ad_count(text):
            errors.append(f"{relative} contains contradictory initial-ad count")
        if permits_automatic_meta_change(text):
            errors.append(
                f"{relative} permits automatic Meta publishing or budget changes"
            )
        if creative_audit_assigns_performance_action(text):
            errors.append(f"{relative} permits Creative Audit performance actions")

    if len(analysis_routing_sections) == 3:
        section_counts = collections.Counter(analysis_routing_sections.values())
        expected_section, expected_count = section_counts.most_common(1)[0]
        if expected_count >= 2:
            for relative, section in analysis_routing_sections.items():
                if section != expected_section:
                    errors.append(
                        f"{relative} ad-analysis routing section has drifted"
                    )
        elif len(section_counts) > 1:
            for relative in analysis_routing_sections:
                errors.append(f"{relative} ad-analysis routing section has drifted")

    version_path = root / "VERSION"
    if version_path.is_file() and version_path.read_text().strip() != "0.4.0":
        errors.append("VERSION must declare 0.4.0")

    for relative in V03_REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing v0.3 required file: {relative}")

    for relative in V04_REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing v0.4 required file: {relative}")

    creative_audit_path = root / "contracts" / "creative-audit.md"
    if creative_audit_path.is_file() and creative_audit_predicts_performance(
        creative_audit_path.read_text()
    ):
        errors.append("contracts/creative-audit.md predicts winning performance")
    if creative_audit_path.is_file() and creative_audit_assigns_performance_action(
        creative_audit_path.read_text()
    ):
        errors.append("contracts/creative-audit.md assigns a performance action")

    creative_example_path = root / "examples" / "creative-audit.md"
    if creative_example_path.is_file() and creative_audit_predicts_performance(
        creative_example_path.read_text()
    ):
        errors.append("examples/creative-audit.md predicts performance")

    diagnosis_path = root / "contracts" / "ad-diagnosis.md"
    if diagnosis_path.is_file() and OPTIONAL_PERFORMANCE_DECISION.search(
        diagnosis_path.read_text()
    ):
        errors.append(
            "contracts/ad-diagnosis.md permits performance decisions without performance data"
        )
    if diagnosis_path.is_file() and not diagnosis_actions_are_governed(
        diagnosis_path.read_text()
    ):
        errors.append("contracts/ad-diagnosis.md must allow only keep, ITR, stop or scale")

    harness_reference = root / "references" / "19-ad-analysis-harness.md"
    if harness_reference.is_file() and AUTOMATIC_CONTST_RESERVATION.search(
        harness_reference.read_text()
    ):
        errors.append(
            "references/19-ad-analysis-harness.md automatically reserves a CONTST"
        )

    harness_path = root / "scripts" / "ad_analysis_harness.py"
    if harness_path.is_file():
        for dependency in harness_imports_are_safe(harness_path):
            errors.append(
                "scripts/ad_analysis_harness.py imports a non-standard or network dependency: "
                f"{dependency}"
            )

    for relative in STANDARD_AD_CONTRACTS:
        path = root / relative
        if path.is_file() and MOST_AWARE_ROW.search(path.read_text()):
            errors.append(f"{relative} contains a Most Aware standard-ad row")

    for path in active_instruction_paths(root):
        if prescribes_most_aware_standard_ad(path.read_text()):
            relative = path.relative_to(root).as_posix()
            errors.append(f"{relative} prescribes a Most Aware standard ad")

    platform_reference = root / "references" / "12-meta-platform.md"
    if platform_reference.is_file():
        platform_text = platform_reference.read_text()
        for pattern, error in LEGACY_PLATFORM_POLICIES:
            if pattern.search(platform_text):
                errors.append(f"references/12-meta-platform.md contains {error}")
        if sets_seven_day_test_default(platform_text):
            errors.append(
                "references/12-meta-platform.md sets a seven-day default test duration"
            )

    validity_reference = root / "references" / "09-testing-and-diagnosis.md"
    if validity_reference.is_file():
        validity_text = validity_reference.read_text()
        validity_section = markdown_section(validity_text, "Read validity")
        matches = [pattern.search(validity_section) for pattern in READ_VALIDITY_RULES]
        if any(match is None for match in matches) or [
            match.start() for match in matches if match is not None
        ] != sorted(match.start() for match in matches if match is not None):
            errors.append(
                "references/09-testing-and-diagnosis.md must define ordered non-overlapping read validity"
            )
        if permits_pre_five_day_verdict(validity_text):
            errors.append(
                "references/09-testing-and-diagnosis.md permits a Verdict before five full days"
            )

    campaign_launch_path = root / CAMPAIGN_LAUNCH_CONTRACT
    if campaign_launch_path.is_file():
        contract = campaign_launch_path.read_text()
        for pattern, error in CREATIVE_TESTING_RULES:
            if not pattern.search(markdown_section(contract, "Creative testing")):
                errors.append(error)
        for pattern, error in SCALING_RULES:
            if not pattern.search(markdown_section(contract, "Scaling")):
                errors.append(error)

    test_register_path = root / TEMPLATE_TEST_REGISTER
    if test_register_path.is_file():
        test_ids = list(CONTST_TEST_ID.finditer(test_register_path.read_text()))
        identifiers = [match.group(1).upper() for match in test_ids]
        seen: set[str] = set()
        for identifier in identifiers:
            if identifier in seen:
                errors.append(f"{TEMPLATE_TEST_REGISTER} reuses {identifier}")
            seen.add(identifier)
        numbers = sorted({int(match.group("number")) for match in test_ids})
        if numbers and numbers != list(range(1, numbers[-1] + 1)):
            errors.append(
                f"{TEMPLATE_TEST_REGISTER} must use sequential CONTST values"
            )

    if skill_path.is_file() and agents_path.is_file():
        if operating_body(skill_text) != operating_body(agents_path.read_text()):
            errors.append("SKILL.md and AGENTS.md operating bodies have drifted")

    examples = root / "examples"
    if examples.is_dir():
        for example in sorted(examples.rglob("*.md")):
            if PLACEHOLDER.search(example.read_text()):
                relative = example.relative_to(root)
                errors.append(f"{relative} contains an unfinished placeholder")

    return errors


def main(argv: list[str]) -> int:
    root = pathlib.Path(argv[1]).resolve() if len(argv) > 1 else pathlib.Path.cwd()
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Package validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
