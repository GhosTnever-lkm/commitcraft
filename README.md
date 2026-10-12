# CommitCraft

CommitCraft turns Git history into a readable Markdown changelog grouped by Conventional Commit type. It runs locally with Python 3.10+ and Git; repository data stays on your machine.

## Install

```bash
python -m pip install "commitcraft @ git+https://github.com/GhosTnever-lkm/commitcraft.git@v1.0.4"
```

## Quick start

From the repository whose history you want to summarize, run:

```bash
commitcraft
```

This writes unreleased notes since the latest reachable tag to the terminal. Review the output, then save it when ready:

```bash
commitcraft --output RELEASE_NOTES.md --title "What's new"
```

Compare two known refs in the target repository:

```bash
commitcraft --repo ../my-project --from v1.2.0 --to v1.3.0 --output RELEASE_NOTES.md
```

`--from` and `--to` are Git refs from the repository being inspected. Replace the example tags with refs that actually exist there. The starting ref is excluded; the ending ref is included.

## Include older history

By default, CommitCraft starts after the latest tag reachable from `--to`. To intentionally include every commit reachable from the target ref:

```bash
commitcraft --all-history --to HEAD
```

To omit commit subjects that do not follow Conventional Commits, add `--conventional-only`. By default, those commits appear under **Other** so they are not silently discarded. Commit bodies containing `BREAKING CHANGE:` and subjects using `!:` appear under **Breaking changes**.

## Categories

`feat` → Features · `fix` → Fixes · `perf` → Performance · `docs` → Documentation · `refactor` → Refactoring · `build` → Build · `ci` → CI · `test` → Tests. Other conventional types receive their own heading.

## Privacy and limits

CommitCraft reads local Git history using the installed Git executable. It does not access the network or change repository files unless `--output` is supplied. It cannot determine whether a commit is user-facing, so review generated notes before publishing them.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
ruff check . && ruff format --check .
mypy commitcraft
```

## License

MIT. See [LICENSE](LICENSE).
