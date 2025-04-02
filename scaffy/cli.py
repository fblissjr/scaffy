# scaffy/cli.py
import argparse
import os
import sys
import textwrap
from scaffy.core import parse_ascii_tree, evaluate_path, actually_create
from scaffy.rules import sanitize_ascii_tree


def main():
    parser = argparse.ArgumentParser(
        description="scaffy: scaffold a project folder structure from an ASCII tree"
    )
    parser.add_argument("--tree-file", help="path to a file with the ascii tree")
    parser.add_argument("--tree-string", help="ascii tree passed directly as a string")
    parser.add_argument(
        "--root-dir", default=".", help="where to create items (default '.')"
    )
    parser.add_argument(
        "--project-name",
        help="name for a minimal default tree (required if no ascii tree is given)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="apply changes without prompting (default is dry-run)",
    )
    parser.add_argument(
        "--comments",
        action="store_true",
        help="include trailing comments in generated files",
    )
    args = parser.parse_args()

    ascii_lines = None
    if args.tree_file:
        with open(args.tree_file, "r", encoding="utf-8") as f:
            ascii_lines = f.readlines()
    elif args.tree_string:
        ascii_lines = args.tree_string.splitlines()
    elif not sys.stdin.isatty():
        ascii_lines = sys.stdin.read().splitlines()

    if not ascii_lines:
        if not args.project_name:
            print(
                "error: no ascii tree provided. please supply a tree or use --project-name."
            )
            sys.exit(1)
        ascii_lines = (
            textwrap.dedent(f"""
        {args.project_name}/
        ├── README.md
        ├── .gitignore
        ├── src/
        │   └── main.py
        └── tests/
            └── test_main.py
        """)
            .strip()
            .splitlines()
        )

    ascii_lines = sanitize_ascii_tree(ascii_lines)
    parsed_paths = parse_ascii_tree(ascii_lines)
    if not parsed_paths:
        print("no valid paths detected. exiting.")
        sys.exit(0)

    records = [evaluate_path(args.root_dir, p) for p in parsed_paths]

    print("\n(dry run) these actions would be performed:\n")
    for r in records:
        print(f"  {r['type']} {r['path']} -> {r['status']}")

    if not args.yes:
        if sys.stdin.isatty():
            try:
                confirm = (
                    input("\ncontinue and apply these changes? [y/N]: ").strip().lower()
                )
                if confirm not in ("y", "yes"):
                    print("aborted.")
                    sys.exit(0)
            except EOFError:
                print(
                    "\nerror: cannot prompt for confirmation in non-interactive mode. use --yes to apply."
                )
                sys.exit(1)
        else:
            print(
                "\nerror: confirmation required in non-interactive mode. use --yes to apply changes."
            )
            sys.exit(1)

    for rec in records:
        actually_create(
            args.root_dir,
            rec["path"],
            rec,
            ascii_lines=ascii_lines,
            with_comments=args.comments,
        )

    print("\ndone.")


if __name__ == "__main__":
    main()
