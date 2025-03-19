#!/bin/bash

shopt -s globstar

for pyfile in dependencies/**/*.py
do
  [ "$(basename "$pyfile")" = "__init__.py" ] && continue

  # Build dotted path, e.g. "dependencies.general.make_relative_file_path"
  mod_path=$(echo "$pyfile" | sed 's|^dependencies/|dependencies.|; s|/|.|g; s|.py$||')

  # Look for lines containing either "import mod_path" or "from mod_path import"
  result=$(grep -rE "import $mod_path(\.| |$)|from $mod_path import" . --include='*.py' 2>/dev/null || true)

  if [ -z "$result" ]; then
    echo "$pyfile"
  fi
done | tee unimported_files.txt

xargs rm < unimported_files.txt
