#!/usr/bin/env python3
"""
HoopShot Policy Checker
Runs automated checks from policies/*.yaml against the codebase.
Manual-review checks are listed but not failed automatically.

Usage:
    python scripts/check_policies.py [--strict]

    --strict: fail on manual-review items too (useful before release)

Exit codes:
    0 — all automated checks pass
    1 — one or more automated checks failed
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(2)

ROOT = Path(__file__).parent.parent
POLICIES_DIR = ROOT / "policies"

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
COLORS = {
    "red": "\033[91m",
    "yellow": "\033[93m",
    "green": "\033[92m",
    "cyan": "\033[96m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


def color(text: str, *codes: str) -> str:
    if sys.stdout.isatty():
        return "".join(COLORS.get(c, "") for c in codes) + text + COLORS["reset"]
    return text


def load_policies() -> list[dict]:
    policies = []
    for f in sorted(POLICIES_DIR.glob("*.yaml")):
        with f.open() as fh:
            data = yaml.safe_load(fh)
            for rule in data.get("rules", []):
                rule["_policy_file"] = f.name
                rule["_policy_name"] = data.get("name", f.stem)
            policies.extend(data.get("rules", []))
    return policies


def get_files(file_types: Optional[list[str]] = None, exclude_paths: Optional[list[str]] = None) -> list[Path]:
    patterns = file_types or ["*.py", "*.ts", "*.tsx", "*.swift"]
    files = []
    for pattern in patterns:
        for p in ROOT.rglob(pattern):
            if any(part.startswith(".") or part in ("node_modules", "__pycache__", ".next", "build")
                   for part in p.parts):
                continue
            if exclude_paths and any(p.is_relative_to(ROOT / ep.lstrip("/")) for ep in exclude_paths):
                continue
            files.append(p)
    return files


def check_pattern_rule(rule: dict) -> list[str]:
    """Search codebase for forbidden patterns. Returns list of violation strings."""
    patterns = rule.get("patterns", [])
    file_types = rule.get("file_types")
    exclude_files = rule.get("exclude_files", [])
    exclude_paths = rule.get("exclude_paths", [])

    violations = []
    for filepath in get_files(file_types, exclude_paths):
        # Check exclude_files globs
        if any(filepath.match(ef) for ef in exclude_files):
            continue
        try:
            text = filepath.read_text(errors="ignore")
        except OSError:
            continue
        for pattern in patterns:
            for lineno, line in enumerate(text.splitlines(), 1):
                if re.search(pattern, line):
                    rel = filepath.relative_to(ROOT)
                    violations.append(f"  {rel}:{lineno}: {line.strip()[:100]}")
    return violations


def check_file_pattern(rule: dict) -> list[str]:
    """Check that a specific file contains a required pattern."""
    file_path = ROOT / rule.get("file", "")
    pattern = rule.get("pattern", "")
    if not file_path.exists():
        return [f"  File not found: {rule.get('file')}"]
    text = file_path.read_text(errors="ignore")
    if not re.search(pattern, text):
        return [f"  Pattern not found in {rule.get('file')}: {pattern}"]
    return []


def run_check(rule: dict) -> tuple:
    """Returns (status, violations). Status: PASS / FAIL / MANUAL / SKIP."""
    check = rule.get("check", "")

    if check == "manual_review":
        return "MANUAL", []

    if check == "informational":
        return "INFO", []

    if check in ("no_hardcoded_secrets", "no_plaintext_password_log",
                 "no_raw_sql_interpolation", "no_bare_except",
                 "no_todo_comments", "no_implicit_any", "no_force_unwrap"):
        violations = check_pattern_rule(rule)
        return ("FAIL", violations) if violations else ("PASS", [])

    if check == "health_endpoint_exists":
        violations = check_file_pattern(rule)
        return ("FAIL", violations) if violations else ("PASS", [])

    if check == "no_committed_secrets":
        gi = ROOT / ".gitignore"
        if not gi.exists():
            return "FAIL", ["  .gitignore not found"]
        gi_text = gi.read_text()
        missing = [p for p in rule.get("patterns", []) if not re.search(p, gi_text, re.MULTILINE)]
        if missing:
            return "FAIL", [f"  Pattern not in .gitignore: {p}" for p in missing]
        return "PASS", []

    if check in ("test_file_exists", "file_exists"):
        f = ROOT / rule.get("file", "")
        if not f.exists():
            return "FAIL", [f"  Missing file: {rule.get('file')}"]
        return "PASS", []

    if check == "gitignore_db":
        gi = ROOT / ".gitignore"
        if not gi.exists():
            return "FAIL", ["  .gitignore not found"]
        if not re.search(rule.get("pattern", r"\.db"), gi.read_text()):
            return "FAIL", ["  .gitignore does not exclude *.db files"]
        return "PASS", []

    # Unknown check type — treat as manual
    return "MANUAL", []


def main():
    parser = argparse.ArgumentParser(description="HoopShot policy checker")
    parser.add_argument("--strict", action="store_true", help="Fail on manual-review items")
    args = parser.parse_args()

    rules = load_policies()
    rules.sort(key=lambda r: SEVERITY_ORDER.get(r.get("severity", "info"), 99))

    failed = 0
    manual = 0

    print(color(f"\n{'='*60}", "bold"))
    print(color("  HoopShot Policy Checker", "bold"))
    print(color(f"{'='*60}\n", "bold"))

    current_policy = None
    for rule in rules:
        policy = rule["_policy_name"]
        if policy != current_policy:
            print(color(f"\n[{rule['_policy_file']}]", "cyan", "bold"))
            current_policy = policy

        status, violations = run_check(rule)
        rule_id = rule.get("id", "?")
        sev = rule.get("severity", "info").upper()
        desc = rule.get("description", "")

        if status == "PASS":
            icon = color("✓", "green")
        elif status == "FAIL":
            icon = color("✗", "red")
            failed += 1
        elif status == "MANUAL":
            icon = color("?", "yellow")
            manual += 1
        else:
            icon = color("i", "cyan")

        sev_colored = color(f"[{sev}]", "red" if sev in ("CRITICAL", "HIGH") else "yellow" if sev == "MEDIUM" else "reset")
        print(f"  {icon} {rule_id} {sev_colored} {desc}")

        if violations:
            for v in violations[:5]:
                print(color(v, "red"))
            if len(violations) > 5:
                print(color(f"  ... and {len(violations) - 5} more", "red"))

        if status == "MANUAL" and rule.get("note"):
            print(color(f"    → {rule['note']}", "yellow"))

    print(color(f"\n{'='*60}", "bold"))
    auto_pass = sum(1 for r in rules if run_check(r)[0] == "PASS")
    print(f"  Automated:   {color(str(auto_pass), 'green')} passed, {color(str(failed), 'red')} failed")
    print(f"  Manual:      {color(str(manual), 'yellow')} require human review")
    print(color(f"{'='*60}\n", "bold"))

    if failed > 0:
        print(color("POLICY CHECK FAILED — fix critical/high issues before merging.\n", "red", "bold"))
        sys.exit(1)
    if args.strict and manual > 0:
        print(color("STRICT MODE: manual reviews required before release.\n", "yellow", "bold"))
        sys.exit(1)
    print(color("All automated policy checks passed.\n", "green", "bold"))
    sys.exit(0)


if __name__ == "__main__":
    main()
