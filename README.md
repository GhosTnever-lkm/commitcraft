# CommitCraft

CommitCraft turns Git history into a clean Markdown changelog, grouped by Conventional Commit type. It runs locally, needs only Python 3.10+ and Git, and sends no repository data anywhere.

## Install

```bash
python -m pip install "commitcraft @ git+https://github.com/GhosTnever-lkm/commitcraft.git@v1.0.2"
```

## Use

Generate unreleased notes since the most recent Git tag:

```bash
commitcraft
```

Compare a specific release tag with the current checkout and save the result:

```bash
commitcraft --from v1.2.0 --to HEAD --output RELEASE_NOTES.md --title "What's new"
```

Use `--all-history` when you intentionally want every commit reachable from the target:

```bash
commitcraft --all-history
```

Run against another repository:

```bash
commitcraft --repo ../my-project --from v1.2.0 --to v1.3.0
```

Use `--conventional-only` to leave out messages that do not match Conventional Commits. By default, those messages are grouped under **Other**, so they are not silently lost. Commit bodies containing `BREAKING CHANGE:` and subjects using `!:` appear under **Breaking changes**.

## Categories

`feat` → Features · `fix` → Fixes · `perf` → Performance · `docs` → Documentation · `refactor` → Refactoring · `build` → Build · `ci` → CI · `test` → Tests. Other conventional types receive their own heading.

## Privacy and limits

CommitCraft reads local Git history using the installed Git executable. It does not access the network, change repository files unless `--output` is supplied, or infer whether a change is user-facing. Review the generated notes before publishing them.

## License

MIT. See [LICENSE](LICENSE).
