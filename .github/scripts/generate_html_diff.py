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

def generate_html_diff(old_lines, new_lines):
    differ = difflib.HtmlDiff(tabsize=4, wrapcolumn=80)
    return differ.make_file(fromlines=old_lines, tolines=new_lines,
                            fromdesc='Previous Version', todesc='Current Version')

base = os.getenv("GITHUB_BASE_REF") or "HEAD~1"
head = "HEAD"

old = get_file_content(base)
new = get_file_content(head)

html_diff = generate_html_diff(old, new)

output_path = "review_diff.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_diff)

print(f"✅ HTML-рецензія збережена у {output_path}")
