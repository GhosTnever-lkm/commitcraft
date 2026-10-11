# Changelog

## v1.0.3

- Add a test suite (23 tests): classification, grouping order, breaking changes, tag ranges, CLI output, error handling. Coverage 99% (pytest-cov).
- CI now runs pytest, ruff (lint + format) and mypy on Python 3.10-3.12, in addition to the install smoke test.
- Fix import order and a deprecated `typing.Iterable` import flagged by ruff; apply ruff formatting.
- Document the development workflow in the README.

## v1.0.2

- Restore the complete standard MIT license, including its limitation-of-liability clause.
- Update the installation example to v1.0.2.


## v1.0.1

- Default to commits after the latest reachable tag instead of labeling the entire history as unreleased.
- Add `--all-history` for an explicit full-history report.

## v1.0.0

- First release: local Git history reader, Conventional Commit grouping, breaking-change detection, Markdown output, and command-line options.
