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

def describe_diff(old_lines, new_lines):
    diff = difflib.unified_diff(old_lines, new_lines, lineterm='')
    changes = []
    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            changes.append(f"➕ Додано: {line[1:]}")
        elif line.startswith('-') and not line.startswith('---'):
            changes.append(f"➖ Видалено: {line[1:]}")
    return '\n'.join(changes) if changes else "✅ Немає змін"

base = os.getenv("GITHUB_BASE_REF") or "HEAD~1"
head = "HEAD"

old = get_file_content(base)
new = get_file_content(head)
summary = describe_diff(old, new)

print("📄 Зміни в Markdown-файлі:\n")
print(summary)
