import difflib
import os
import subprocess

FILE_PATH = os.getenv("MARKDOWN_FILE", "README.md")

def get_file_content(ref):
    try:
        result = subprocess.run(
            ["git", "show", f"{ref}:{FILE_PATH}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError:
        return []

def format_review_diff(old_lines, new_lines):
    differ = difflib.Differ()
    diff = list(differ.compare(old_lines, new_lines))
    result = []
    for line in diff:
        if line.startswith("- "):
            result.append(f"~~{line[2:]}~~")  # закреслене (видалене)
        elif line.startswith("+ "):
            result.append(f"**{line[2:]}**")  # жирне (додане)
        elif line.startswith("  "):
            result.append(line[2:])  # незмінений текст
    return "\n".join(result)

base = os.getenv("GITHUB_BASE_REF") or "HEAD~1"
head = "HEAD"

old = get_file_content(base)
new = get_file_content(head)

formatted = format_review_diff(old, new)
print("📝 **Зміни з рецензією**:\n")
print(formatted)
