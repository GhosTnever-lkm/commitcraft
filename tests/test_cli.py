"""End-to-end tests for the command line interface."""

import subprocess
from pathlib import Path

from conftest import commit

from commitcraft import __version__
from commitcraft.cli import main


def test_cli_prints_changelog(repo, capsys):
    commit(repo, "feat: shiny")
    assert main(["--repo", str(repo)]) == 0
    out = capsys.readouterr().out
    assert "# Unreleased" in out
    assert "shiny" in out


def test_cli_writes_output_file(repo, tmp_path, capsys):
    commit(repo, "fix: patched")
    output = tmp_path / "NOTES.md"
    assert main(["--repo", str(repo), "--output", str(output)]) == 0
    assert "patched" in output.read_text(encoding="utf-8")
    assert "Wrote" in capsys.readouterr().out


def test_cli_conventional_only(repo, capsys):
    commit(repo, "no convention here")
    assert main(["--repo", str(repo), "--conventional-only"]) == 0
    assert "No commits found" in capsys.readouterr().out


def test_cli_bad_repo_returns_2(tmp_path, capsys):
    assert main(["--repo", str(tmp_path / "missing")]) == 2
    assert "commitcraft:" in capsys.readouterr().err


def test_cli_revision_cannot_write_to_a_git_option_path(repo, tmp_path, capsys):
    commit(repo, "feat: keep target repository unchanged")
    output = tmp_path / "unexpected-output.txt"

    assert main(["--repo", str(repo), f"--to=--output={output}"]) == 2
    assert not output.exists()
    assert "commitcraft:" in capsys.readouterr().err


def test_cli_version(capsys):
    import pytest

    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out == f"commitcraft {__version__}\n"


def test_readme_install_pin_matches_cli_version():
    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
    assert f"commitcraft.git@v{__version__}" in readme


def test_console_script_entrypoint(repo):
    import sys
    from pathlib import Path

    script = Path(sys.executable).with_name("commitcraft")
    if not script.exists():
        import pytest

        pytest.skip("console script not installed in this environment")
    commit(repo, "feat: via console script")
    result = subprocess.run(
        [str(script), "--repo", str(repo), "--title", "Notes"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("# Notes")
