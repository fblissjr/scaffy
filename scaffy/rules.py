# scaffy/rules.py
import re
from typing import List

def normalize_slashes(path: str) -> str:
    return path.replace('\\', '/').strip()

def is_absolute_path(path: str) -> bool:
    return path.startswith('/') or re.match(r'^[a-zA-Z]:\\', path)

def is_suspicious_file_root(path: str) -> bool:
    return path.endswith('.py') or '.' in path.split('/')[-1]

def normalize_root_line(line: str) -> str:
    """
    Normalize the root line:
    - Convert backslashes to slashes
    - Strip leading ./
    - Detect and reject absolute paths
    """
    line = normalize_slashes(line.strip())

    if not line or line == '.':
        return ''  # current folder root
    if is_absolute_path(line):
        raise ValueError(f"absolute path not allowed as root: {line}")
    return line.lstrip('./')

def sanitize_ascii_tree(lines: List[str]) -> List[str]:
    """
    Normalize the first root line and return the tree with it updated.
    Also supports trees that start directly with child lines (├── ...)
    """
    if not lines:
        return []

    first = lines[0].strip()

    if first == ".":
        return lines[1:]  # drop explicit current dir

    if first.startswith(("├", "└", "│", " ")):
        return lines  # treat as relative to cwd

    normalized_root = normalize_root_line(first)

    if not normalized_root:
        return lines[1:]
    else:
        lines[0] = (
            normalized_root + "/"
            if not normalized_root.endswith("/")
            else normalized_root
        )
        return lines
