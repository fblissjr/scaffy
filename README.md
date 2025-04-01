# scaffold-project

a small utility cli that reads an ascii folder tree like the one [below in this readme](#project-tree)) from stdin, a file, or a string, and creates directories and files accordingly. it won't overwrite existing files. if no input is provided, it errors and does nothing.

## usage examples

- read tree from file:
  ```bash
  cat my_tree.txt | scaffy
  ```

- grep an existing file and pipe it:
  ```bash
  grep 'myapp' my_tree.txt | scaffy
  ```

- read from mac clipboard:
  ```bash
  pbpaste | scaffy
  ```

- if no ascii tree is supplied:
  ```bash
  scaffy --project-name cool_app_name
  ```

- pass a tree string directly, but doing this is probably insane and you're better off just piping it in:
  ```bash
  scaffy --tree-string "myapp/\n├── config.py"
  ```

- dry run (shows what would be created, doesn't write anything):
  ```bash
  scaffy --project-name cool_app --dry-run
  ```

- help:
  ```bash
  scaffy --help
  ```