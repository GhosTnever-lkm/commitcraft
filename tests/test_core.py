"""Unit tests for commit classification, rendering, and range selection."""

from conftest import commit, git

from commitcraft.core import Commit, classify, generate, git_commits, latest_tag, render


class TestClassify:
    def test_conventional_types_map_to_groups(self):
        entry = classify(Commit("abc1234", "feat: add dark mode"))
        assert entry.category == "Features"
        assert entry.subject == "add dark mode"
        entry = classify(Commit("abc1234", "fix(cli): handle empty history"))
        assert entry.category == "Fixes"
        assert entry.scope == "cli"

    def test_breaking_marker_on_subject(self):
        entry = classify(Commit("abc1234", "feat!: drop Python 3.9"))
        assert entry.category == "Breaking changes"
        assert entry.breaking

    def test_breaking_change_in_body(self):
        entry = classify(Commit("abc1234", "feat: new API", "BREAKING CHANGE: old API removed"))
        assert entry.category == "Breaking changes"

    def test_unknown_commit_goes_to_other(self):
        entry = classify(Commit("abc1234", "tweaked stuff"))
        assert entry.category == "Other"

    def test_unknown_commit_excluded_when_conventional_only(self):
        assert classify(Commit("abc1234", "tweaked stuff"), include_unknown=False) is None

    def test_unmapped_type_gets_own_heading(self):
        entry = classify(Commit("abc1234", "security: patch CVE-2024-1"))
        assert entry.category == "Security"


class TestRender:
    def test_empty_range(self):
        assert render([], "Notes") == "# Notes\n\nNo commits found in this range.\n"

    def test_groups_in_priority_order(self):
        entries = [
            classify(Commit("aaa1111", "docs: update readme")),
            classify(Commit("bbb2222", "feat: new flag")),
            classify(Commit("ccc3333", "fix: crash on empty input")),
        ]
        markdown = render(entries)
        assert markdown.index("## Features") < markdown.index("## Fixes")
        assert markdown.index("## Fixes") < markdown.index("## Documentation")
        assert "- new flag ([bbb2222])" in markdown

    def test_scope_is_rendered_in_bold(self):
        markdown = render([classify(Commit("abc1234", "fix(cli): bad exit code"))])
        assert "**cli:** bad exit code" in markdown


class TestGitIntegration:
    def test_git_commits_reads_subjects_and_bodies(self, repo):
        commit(repo, "feat: first", "body line")
        commit(repo, "fix: second")
        commits = git_commits(str(repo), "HEAD")
        assert [c.subject for c in commits] == ["feat: first", "fix: second"]
        assert commits[0].body == "body line"
        assert len(commits[0].short_hash) >= 7

    def test_git_commits_reports_errors(self, repo):
        import pytest

        with pytest.raises(RuntimeError):
            git_commits(str(repo), "no-such-ref")

    def test_revision_cannot_inject_git_output_option(self, repo, tmp_path):
        import pytest

        commit(repo, "feat: keep history read only")
        output = tmp_path / "unexpected-output.txt"
        injected_revision = f"--output={output}"

        assert latest_tag(str(repo), injected_revision) is None
        with pytest.raises(RuntimeError):
            git_commits(str(repo), injected_revision)
        assert not output.exists()

    def test_latest_tag_none_without_tags(self, repo):
        commit(repo, "feat: one")
        assert latest_tag(str(repo), "HEAD") is None

    def test_latest_tag_found(self, repo):
        commit(repo, "feat: one")
        git(repo, "tag", "v1.0.0")
        commit(repo, "fix: two")
        assert latest_tag(str(repo), "HEAD") == "v1.0.0"

    def test_generate_since_latest_tag(self, repo):
        commit(repo, "feat: old")
        git(repo, "tag", "v1.0.0")
        commit(repo, "fix: fresh fix")
        markdown = generate(str(repo))
        assert "since v1.0.0" in markdown
        assert "fresh fix" in markdown
        assert "old" not in markdown

    def test_generate_all_history(self, repo):
        commit(repo, "feat: old")
        git(repo, "tag", "v1.0.0")
        commit(repo, "feat: new thing")
        markdown = generate(str(repo), all_history=True)
        assert "old" in markdown and "new thing" in markdown

    def test_generate_explicit_range_and_title(self, repo):
        commit(repo, "feat: one")
        git(repo, "tag", "v1.0.0")
        commit(repo, "feat: two")
        markdown = generate(str(repo), from_ref="v1.0.0", title="What's new")
        assert markdown.startswith("# What's new")
        assert "two" in markdown and "one" not in markdown

    def test_generate_conventional_only(self, repo):
        commit(repo, "miscellaneous fiddling")
        markdown = generate(str(repo), include_unknown=False)
        assert "No commits found" in markdown
