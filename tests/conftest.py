import subprocess

import pytest


def git(repo, *args):
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def commit(repo, subject, body=""):
    (repo / "file.txt").write_text(subject, encoding="utf-8")
    git(repo, "add", "file.txt")
    message = subject if not body else f"{subject}\n\n{body}"
    git(
        repo,
        "-c",
        "user.name=Tester",
        "-c",
        "user.email=tester@example.com",
        "commit",
        "-m",
        message,
    )


@pytest.fixture
def repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    return repo
