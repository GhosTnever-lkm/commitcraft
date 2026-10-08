"""Git history parsing and Markdown rendering."""

from __future__ import annotations

from dataclasses import dataclass
import re
import subprocess
from typing import Iterable

CONVENTIONAL = re.compile(
    r"^(?P<type>[a-zA-Z][a-zA-Z0-9_-]*)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<subject>.+)$"
)
GROUPS = {
    "feat": "Features",
    "feature": "Features",
    "fix": "Fixes",
    "bugfix": "Fixes",
    "perf": "Performance",
    "refactor": "Refactoring",
    "docs": "Documentation",
    "doc": "Documentation",
    "build": "Build",
    "ci": "CI",
    "test": "Tests",
    "tests": "Tests",
    "style": "Styling",
    "revert": "Reverts",
}


@dataclass(frozen=True)
class Commit:
    short_hash: str
    subject: str
    body: str = ""


@dataclass(frozen=True)
class Entry:
    category: str
    scope: str
    subject: str
    short_hash: str
    breaking: bool = False


def git_commits(repo: str, revision: str) -> list[Commit]:
    """Read commits with NUL-delimited fields to preserve punctuation safely."""
    command = [
        "git", "-C", repo, "log", "--no-merges", "--reverse",
        "--format=%h%x00%s%x00%b%x00", revision,
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode:
        message = result.stderr.strip() or "git log failed"
        raise RuntimeError(message)
    fields = result.stdout.split("\x00")
    commits = []
    for i in range(0, len(fields) - 2, 3):
        short_hash, subject, body = fields[i:i + 3]
        if short_hash and subject:
            commits.append(Commit(short_hash.strip(), subject.strip(), body.strip()))
    return commits


def classify(commit: Commit, include_unknown: bool = True) -> Entry | None:
    match = CONVENTIONAL.match(commit.subject)
    if not match:
        return Entry("Other", "", commit.subject, commit.short_hash) if include_unknown else None
    kind = match.group("type").lower()
    breaking = bool(match.group("breaking")) or bool(
        re.search(r"(?im)^BREAKING CHANGE(?:S)?:\s*\S", commit.body)
    )
    category = "Breaking changes" if breaking else GROUPS.get(kind, kind.replace("-", " ").title())
    return Entry(category, match.group("scope") or "", match.group("subject").strip(), commit.short_hash, breaking)


def render(entries: Iterable[Entry], title: str = "Changelog") -> str:
    entries = list(entries)
    if not entries:
        return f"# {title}\n\nNo commits found in this range.\n"
    priority = ["Breaking changes", "Features", "Fixes", "Performance", "Refactoring", "Documentation", "Build", "CI", "Tests", "Styling", "Reverts", "Other"]
    categories = sorted({entry.category for entry in entries}, key=lambda name: (priority.index(name) if name in priority else len(priority), name.casefold()))
    lines = [f"# {title}", ""]
    for category in categories:
        lines.extend([f"## {category}", ""])
        group = [entry for entry in entries if entry.category == category]
        for entry in group:
            label = f"**{entry.scope}:** " if entry.scope else ""
            lines.append(f"- {label}{entry.subject} ([{entry.short_hash}])")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate(repo: str, from_ref: str | None = None, to_ref: str = "HEAD", include_unknown: bool = True, title: str | None = None) -> str:
    if from_ref:
        revision = f"{from_ref}..{to_ref}"
        heading = title or f"Changes since {from_ref}"
    else:
        revision = to_ref
        heading = title or "Unreleased"
    commits = git_commits(repo, revision)
    entries = [entry for commit in commits if (entry := classify(commit, include_unknown)) is not None]
    return render(entries, heading)
