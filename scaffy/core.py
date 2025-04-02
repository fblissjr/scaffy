# scaffy/core.py
import os
import re
from typing import List, Dict, Optional

def get_indentation_level(line: str) -> int:
    match = re.match(r'^[\s│├└─]+', line)
    return len(match.group(0)) if match else 0

def split_comment(line: str) -> tuple[str, Optional[str]]:
    if "#" in line:
        base, comment = line.split("#", 1)
        return base.rstrip(), comment.strip()
    return line, None

def parse_ascii_tree(ascii_lines: List[str]) -> List[str]:
    parsed_full_paths = []
    dir_stack = []

    for line in ascii_lines:
        raw_line, _ = split_comment(line.rstrip("\n"))
        if not raw_line.strip():
            continue

        indent = get_indentation_level(raw_line)
        line_no_ascii = re.sub(r"^[\s│├└─]+", "", raw_line).strip()
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

def actually_create(
    base_dir: str,
    path: str,
    record: Dict,
    ascii_lines: Optional[List[str]] = None,
    with_comments: bool = False,
) -> None:
    abs_path = os.path.join(base_dir, path)
    if record["status"] == "created":
        if record["type"] == "directory":
            os.makedirs(abs_path, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            comment = None
            if with_comments and ascii_lines is not None:
                # Try to find matching line and get comment
                for line in ascii_lines:
                    if path in line:
                        _, comment = split_comment(line)
                        break
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(f"# {path}\n")
                if with_comments and comment:
                    f.write(f"# {comment}\n")