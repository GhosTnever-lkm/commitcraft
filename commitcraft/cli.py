"""Command line interface."""

import argparse
from pathlib import Path
import sys

from . import __version__
from .core import generate


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="commitcraft",
        description="Turn Git history into a grouped Markdown changelog.",
        epilog="Example: commitcraft --from v1.2.0 --to HEAD --output CHANGELOG.md",
    )
    result.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    result.add_argument("--repo", default=".", help="Path to a Git repository (default: current directory).")
    result.add_argument("--from", dest="from_ref", help="Starting tag or revision, excluded from the range.")
    result.add_argument("--to", default="HEAD", help="Ending tag or revision (default: HEAD).")
    result.add_argument("--output", help="Write Markdown to this path instead of stdout.")
    result.add_argument("--title", help="Custom Markdown title.")
    result.add_argument("--conventional-only", action="store_true", help="Skip commits that do not follow Conventional Commits.")
    result.add_argument("--all-history", action="store_true", help="Include all commits reachable from --to, ignoring the latest tag.")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        markdown = generate(
            args.repo,
            from_ref=args.from_ref,
            to_ref=args.to,
            include_unknown=not args.conventional_only,
            title=args.title,
            all_history=args.all_history,
        )
        if args.output:
            output = Path(args.output)
            output.write_text(markdown, encoding="utf-8", newline="\n")
            print(f"Wrote {output}")
        else:
            sys.stdout.write(markdown)
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"commitcraft: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
