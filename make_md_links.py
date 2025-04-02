# make_md_links.py
import os
import re
import subprocess
import glob

MARKDOWN_LUA = "/Users/tobias/.config/nvim/lua/luasnippets/markdown.lua"
REPO_URL = "https://github.com/kletobias/advanced-mlops-lifecycle-hydra-mlflow-optuna-dvc/tree/main"


def main():
    # Gather the list of tracked files from Git
    result = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
    file_list = [
        f.strip()
        for f in result.stdout.split("\n")
        if f.strip()
        and not f.endswith(".yaml.dvc")
        and not f.endswith("__init__.py")
        and not f.endswith(".pyc")
    ]
    num_files_in_file_list = len(file_list)
    assert num_files_in_file_list != 0, "Not files in file_list"
    print(num_files_in_file_list)


    # Prepare snippet definitions and references
    snippet_defs = []
    snippet_refs = []
    for path in file_list:
        base = os.path.basename(path)
        if base == 'base':
            base = os.path.pardir.strip() + '_' + base

        base = re.sub(r'^[\d_]+','', base)
        # Turn e.g. "config.yaml" -> snippet__config_yaml
        var_name = base + re.sub(r"[^a-zA-Z0-9]", "_", "snippet")
        # Snippet trigger = same transform, or if you prefer to keep dots, etc., adjust here
        snippet_trigger = base + re.sub(r"[^a-zA-Z0-9]", "_", "snippet")
        # Build snippet definition
        snippet_def = f'{var_name} = s("{snippet_trigger}", {{ t("[{path}]({REPO_URL}/{path})") }})\n'  # line 38 changed (removed 'local ' at the start)
        snippet_defs.append(snippet_def)
        # Build snippet reference for the add_snippets call
        snippet_refs.append(f"  {var_name},")

    # Read original markdown.lua into memory
    with open(MARKDOWN_LUA, "r") as f:
        lines = f.readlines()

    # We'll insert our "local snippet_..." definitions just before the 'ls.add_snippets("markdown", {'
    # Then we'll rebuild the snippet array in that call to include mdcode + our snippet refs
    add_snippets_start = None
    add_snippets_end = None

    # Identify start/end lines for the block that begins with ls.add_snippets("markdown", {
    # and ends with the matching "})".
    brace_depth = 0
    found_block = False
    for i, line in enumerate(lines):
        if 'ls.add_snippets("markdown"' in line:
            add_snippets_start = i
            found_block = True
            # We will track brace depth from here forward
            # Count how many '{' are on this line
            brace_depth += line.count("{") - line.count("}")
            continue
        if found_block:
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0:
                add_snippets_end = i
                break

    # If we couldn't identify a snippet block, we'll just append at the end
    if add_snippets_start is None or add_snippets_end is None:
        # Minimal fallback: put definitions at top and a fresh call at bottom
        new_content = []
        new_content.extend(lines)
        new_content.append("\n-- Added snippet definitions\n")
        new_content.extend(snippet_defs)
        new_content.append('\nls.add_snippets("markdown", {\n  mdcode,\n')
        new_content.extend(s + "\n" for s in snippet_refs)
        new_content.append("})\n\nreturn {}\n")
    else:
        # We'll keep everything up to add_snippets_start as is
        new_content = lines[:add_snippets_start]

        # Insert our snippet definitions
        new_content.append("\n-- Auto-generated snippet definitions\n")
        new_content.extend(snippet_defs)
        new_content.append("\n")

        # Now rewrite ls.add_snippets("markdown", { ... }) portion
        # We'll preserve the line that starts it but strip everything after the '{'
        # so we can re-inject mdcode + snippet references.

        snippet_start_line = lines[add_snippets_start].rstrip("\n")
        # Example: ls.add_snippets("markdown", { mdcode })
        # We want up to 'ls.add_snippets("markdown", {' then newline
        brace_index = snippet_start_line.find("{")
        header_line = snippet_start_line[: brace_index + 1]
        new_content.append(header_line + "\n")

        # We re-inject the snippet array:
        new_content.append("  mdcode,\n")
        for ref in snippet_refs:
            new_content.append(ref + "\n")

        new_content.append("})\n")

        # Then skip lines up through add_snippets_end (that block is replaced)
        # Keep everything else after
        new_content.extend(lines[add_snippets_end:])

    # Write out the updated file
    with open(MARKDOWN_LUA + ".new", "w") as f:
        f.writelines(new_content)

    # Replace original with the new one
    os.replace(MARKDOWN_LUA + ".new", MARKDOWN_LUA)


if __name__ == "__main__":
    main()
