import os
import re
import subprocess

MARKDOWN_LUA = "/Users/tobias/.config/nvim/lua/luasnippets/markdown.lua"
REPO_URL = "https://github.com/kletobias/advanced-mlops-lifecycle-hydra-mlflow-optuna-dvc/tree/main"

def main():
    result = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
    file_list = [
        f.strip()
        for f in result.stdout.split("\n")
        if f.strip()
        and not f.endswith(".yaml.dvc")
        and not f.endswith("__init__.py")
        and not f.endswith(".pyc")
    ]
    assert file_list, "No files found from git ls-files."

    snippet_defs = []
    snippet_refs = []
    for path in file_list:
        parent_dir = os.path.basename(os.path.dirname(path))
        basename   = os.path.basename(path)

        # Remove leading digits and underscores from parent directory
        parent_dir = re.sub(r'^[\d_]+', '', parent_dir)

        # Split off extension for the base filename
        base_no_ext, _ = os.path.splitext(basename)
        # Also remove leading digits/underscores
        base_no_ext = re.sub(r'^[\d_]+', '', base_no_ext)

        # If it's literally "base", prepend the cleaned parent directory
        if base_no_ext == "base" and parent_dir:
            snippet_core = f"{parent_dir}_{base_no_ext}"
        else:
            snippet_core = base_no_ext

        # Final variable name and trigger: <snippet_core>_snippet
        # (keeps "_snippet" at the end so it won't auto-complete on "snip")
        var_name        = snippet_core + "_snippet"
        snippet_trigger = snippet_core + "_snippet"

        # Build snippet definition
        snippet_def = (
            f'{var_name} = s("{snippet_trigger}", '
            f'{{ t("[{path}]({REPO_URL}/{path})") }})\n'
        )
        snippet_defs.append(snippet_def)
        snippet_refs.append(f"  {var_name},")

    # Read original lua file
    with open(MARKDOWN_LUA, "r") as f:
        lines = f.readlines()

    add_snippets_start = None
    add_snippets_end   = None

    # Find the ls.add_snippets("markdown" block
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

    # If we can't find that block, we append at the end
    if add_snippets_start is None or add_snippets_end is None:
        new_content = []
        new_content.extend(lines)
        new_content.append("\n-- Added snippet definitions\n")
        new_content.extend(snippet_defs)
        new_content.append('\nls.add_snippets("markdown", {\n  mdcode,\n')
        new_content.extend(s + "\n" for s in snippet_refs)
        new_content.append("})\n\nreturn {}\n")
    else:
        # Keep everything up to add_snippets_start
        new_content = lines[:add_snippets_start]
        # Insert new snippet definitions
        new_content.append("\n-- Auto-generated snippet definitions\n")
        new_content.extend(snippet_defs)
        new_content.append("\n")

        # Rebuild the snippet block
        start_line      = lines[add_snippets_start].rstrip("\n")
        brace_index     = start_line.find("{")
        header_line     = start_line[: brace_index + 1]
        new_content.append(header_line + "\n")
        new_content.append("  mdcode,\n")
        for ref in snippet_refs:
            new_content.append(ref + "\n")
        new_content.append("})\n")

        # Append everything after the old snippet block
        new_content.extend(lines[add_snippets_end:])

    # Write the updated file
    with open(MARKDOWN_LUA + ".new", "w") as f:
        f.writelines(new_content)
    os.replace(MARKDOWN_LUA + ".new", MARKDOWN_LUA)

if __name__ == "__main__":
    main()
