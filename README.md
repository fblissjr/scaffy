# scaffy

a small utility cli that reads an ascii folder tree (see below format examples) from stdin, a file, or a string, and creates directories and files accordingly. it won't overwrite existing files. if no input is provided, it errors and does nothing.

![svg icon of scaffy mascot](https://github.com/user-attachments/assets/886314f2-bac0-43ee-b9aa-5c0c1cb61135) <- this is scaffy


## usage examples

your project trees should be formatted like this if you're in the parent / root folder, with the `.` at the top indicating current folder as parent. if you want to create the parent as well, you'd just change the `.` to something like `app-cigar-project`.

## normalization rules

| case | example | result |
|------|---------|--------|
| current folder as root | `.` | strip and use `--root-dir` as base |
| relative path with dot | `./foo/bar` | normalize to `foo/bar/` |
| relative path no dot | `foo/bar` | keep as-is |
| empty string | *(empty first line)* | ignore or warn |
| absolute path | `/usr/foo` | reject (outside workspace) |
| file-looking root | `myapp.py` | (suspicious for root folder) |
| multiple levels without dot | `foo/bar/baz/` | valid, preserved |
| windows slashes | `foo\bar` | normalize to `foo/bar` or reject |

### Example with parent folder as current folder
```
.
├── cli.py
├── LICENSE
├── main.py
├── presets
│   └── presets_file.json
├── presets.py
├── README.md
└── utils.py
```

### example for creating passing in the parent as well:

```

├── cli.py
├── LICENSE
├── main.py
├── presets
│   └── presets_file.json
├── presets.py
├── README.md
└── utils.py
```

- read tree from file:
  ```bash
  cat project_tree.txt | scaffy
  ```

- grep an existing file and pipe it:
  ```bash
  grep 'app-cigar-project' project_tree.txt | scaffy
  ```

- read from mac clipboard:
  ```bash
  pbpaste | scaffy
  ```

- if no ascii tree is supplied:
  ```bash
  scaffy --project-name ape-cigar
  ```

- pass a tree string directly, but doing this is probably insane and you're better off just piping it in:
  ```bash
  scaffy --tree-string "app-cigar-project/\n├── config.py"
  ```

- dry run (shows what would be created, doesn't write anything):
  ```bash
  scaffy --project-name app-cigar-project --dry-run
  ```

- help:
  ```bash
  scaffy --help
  ```