import argparse
import os
import sys
import textwrap
import re
from typing import List, Dict

def get_indentation_level(line: str) -> int:
    match = re.match(r'^[\s│├└─]+', line)
    return len(match.group(0)) if match else 0

def parse_ascii_tree(ascii_lines: List[str]) -> List[str]:
    parsed_full_paths = []
    dir_stack = []

    for line in ascii_lines:
        raw = line.rstrip('\n')
        if not raw.strip():
            continue

        indent = get_indentation_level(raw)
        line_no_ascii = re.sub(r'^[\s│├└─]+', '', raw).strip()
        if not line_no_ascii:
            continue

        level = indent // 4
        is_directory = line_no_ascii.endswith('/')
        name = line_no_ascii.rstrip('/') if is_directory else line_no_ascii

        while len(dir_stack) > level:
            dir_stack.pop()

        if is_directory:
            full_path = f"{'/'.join(dir_stack)}/{name}/" if dir_stack else f"{name}/"
            parsed_full_paths.append(full_path)
            dir_stack.append(name)
        else:
            full_path = f"{'/'.join(dir_stack)}/{name}" if dir_stack else name
            parsed_full_paths.append(full_path)

    return parsed_full_paths

def evaluate_path(base_dir: str, path: str) -> Dict:
    abs_path = os.path.join(base_dir, path)
    is_dir = path.endswith('/')
    object_type = "directory" if is_dir else "file"

    if os.path.exists(abs_path):
        return {"path": path, "type": object_type, "status": "skipped", "reason": "exists"}
    return {"path": path, "type": object_type, "status": "created", "reason": None}

def actually_create(base_dir: str, path: str, record: Dict) -> None:
    abs_path = os.path.join(base_dir, path)
    if record["status"] == "created":
        if record["type"] == "directory":
            os.makedirs(abs_path, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(f"# {path}\n")

def main():
    parser = argparse.ArgumentParser(
        description="scaffy: read an ascii tree and create dirs/files accordingly."
    )
    parser.add_argument("--tree-file", help="path to a file with the ascii tree")
    parser.add_argument("--tree-string", help="ascii tree passed directly as a string")
    parser.add_argument(
        "--root-dir", default=".", help="where to create items (default '.')"
    )
    parser.add_argument("--project-name", help="name for a minimal default tree (required if no ascii tree is given)")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="apply changes without prompting (default is dry-run)",
    )
    args = parser.parse_args()

    ascii_lines = None
    if args.tree_file:
        if not os.path.exists(args.tree_file):
            print(f"error: file '{args.tree_file}' does not exist.")
            sys.exit(1)
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
            .strip("\n")
            .splitlines()
        )

    parsed_paths = parse_ascii_tree(ascii_lines)
    if not parsed_paths:
        print("no valid paths detected. exiting.")
        sys.exit(0)

    records = [evaluate_path(args.root_dir, p) for p in parsed_paths]

    print("\n(dry run) these actions would be performed:\n")
    for r in records:
        status = "create" if r["status"] == "created" else "skip"
        print(f"  {r['type']} {r['path']} -> {status}")

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
        actually_create(args.root_dir, rec["path"], rec)

    created = [r for r in records if r["status"] == "created"]
    skipped = [r for r in records if r["status"] == "skipped"]
    print("\nscaffold summary:")
    print(f"  created: {len(created)}")
    print(f"  skipped: {len(skipped)}")

    print("\ndetailed log:")
    for r in records:
        status = "created" if r["status"] == "created" else "skipped"
        info = f"{r['type']} {r['path']} -> {status}"
        if r["reason"]:
            info += f" (reason: {r['reason']})"
        print(f"  {info}")

if __name__ == "__main__":
    main()