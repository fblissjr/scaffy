# scaffy/core.py
import os
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
