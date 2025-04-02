import os
import re
import subprocess

MARKDOWN_LUA = "/Users/tobias/.config/nvim/lua/luasnippets/markdown.lua"
REPO_URL = "https://github.com/kletobias/advanced-mlops-lifecycle-hydra-mlflow-optuna-dvc/tree/main"

def sanitize_for_lua(name: str) -> str:
    # Remove all leading characters that are not letters
    name = re.sub(r'^[^a-zA-Z]+', '', name)
    # Replace any remaining non-alphanumeric chars with underscores
    name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    # Fallback if empty
    if not name:
        name = "file"
    return name

def main():
    # Gather tracked files
    result = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
    file_list = [
        f.strip()
        for f in result.stdout.split("\n")
        if f.strip()
        and not f.endswith(".yaml.dvc")
        and not f.endswith("__init__.py")
        and not f.endswith(".pyc")
    ]
    if not file_list:
        print("No files found")
        return

    # We'll track snippet var names so we can avoid duplicates
    used_names = set()

    snippet_defs = []
    snippet_refs = []

    for path in file_list:
        parent_dir = os.path.basename(os.path.dirname(path))
        basename   = os.path.basename(path)
        base_no_ext, ext = os.path.splitext(basename)

        # Strip leading non-alpha from parent and base
        parent_dir  = sanitize_for_lua(parent_dir)
        base_no_ext = sanitize_for_lua(base_no_ext)

        # If the file is literally named "base" (after sanitize) and there's a parent, combine them
        if base_no_ext.lower() == "base" and parent_dir:
            snippet_core = f"{parent_dir}_{base_no_ext}"
        else:
            snippet_core = base_no_ext

        # Final name: remove the extension from snippet_core if it ended up with leftover underscores
        # (Not strictly necessary, but helps keep it short.)
        snippet_name = snippet_core

        # Guarantee no collisions in snippet_name
        original_name = snippet_name
        i = 2
        while snippet_name in used_names:
            snippet_name = f"{original_name}_{i}"
            i += 1
        used_names.add(snippet_name)

        # The Lua variable and snippet trigger both end with _snippet
        lua_var_name    = snippet_name + "_snippet"
        snippet_trigger = snippet_name + "_snippet"

        snippet_def = (
            f'{lua_var_name} = s("{snippet_trigger}", '
            f'{{ t("[{path}]({REPO_URL}/{path})") }})\n'
        )
        snippet_defs.append(snippet_def)
        snippet_refs.append(f"  {lua_var_name},")

    with open(MARKDOWN_LUA, "r") as f:
        lines = f.readlines()

    add_snippets_start = None
    add_snippets_end   = None
    brace_depth = 0
    found_block = False

    for i, line in enumerate(lines):
        if 'ls.add_snippets("markdown"' in line:
            add_snippets_start = i
            found_block = True
            brace_depth += line.count("{") - line.count("}")
            continue
        if found_block:
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0:
                add_snippets_end = i
                break

    if add_snippets_start is None or add_snippets_end is None:
        # Fallback: put definitions at top and a fresh snippet call at bottom
        new_content = []
        new_content.extend(lines)
        new_content.append("\n-- Auto-generated snippet definitions\n")
        new_content.extend(snippet_defs)
        new_content.append('\nls.add_snippets("markdown", {\n  mdcode,\n')
        new_content.extend(s + "\n" for s in snippet_refs)
        new_content.append("})\n\nreturn {}\n")
    else:
        # Keep everything up to add_snippets_start
        new_content = lines[:add_snippets_start]
        new_content.append("\n-- Auto-generated snippet definitions\n")
        new_content.extend(snippet_defs)
        new_content.append("\n")

        start_line = lines[add_snippets_start].rstrip("\n")
        brace_index = start_line.find("{")
        header_line = start_line[: brace_index + 1]
        new_content.append(header_line + "\n")
        new_content.append("  mdcode,\n")
        for ref in snippet_refs:
            new_content.append(ref + "\n")
        new_content.append("})\n")

        # Append lines after the snippet block
        new_content.extend(lines[add_snippets_end:])

    with open(MARKDOWN_LUA + ".new", "w") as f:
        f.writelines(new_content)

    os.replace(MARKDOWN_LUA + ".new", MARKDOWN_LUA)

if __name__ == "__main__":
    main()
