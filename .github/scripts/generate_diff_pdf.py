import argparse
import subprocess
from pathlib import Path
import re
from weasyprint import HTML
import os

### Generate PDF and HTML with information about changes in repository:
# generate_diff_pdf.py [-h] [--count COUNT] [--compare-commits OLD NEW] [--last-pr] [--mode {simple,full}] [--output-dir OUTPUT_DIR]
#                             [--filename-template FILENAME_TEMPLATE]
#
#
### EXAMPLE:
# python generate_diff_pdf.py 
# generate PDF and HTML with a list of changes at last commit
# all create file place in output dir

# python generate_diff_pdf.py --output-dir out/ --count 5
# generate PDF and HTML with a list of changes at last 5 commits  
# all create file place in "out" dir
#
# python generate_diff_pdf.py --compare-commits 0fd5b2f97a57d25de63f0c8becad659d5b248df1 f0d972b550066c837aa7b203946e91a8c65c52b7
# generate PDF and HTML with all changes before two commits 



def parse_args():
    parser = argparse.ArgumentParser(description="Generate PDF from git diffs.")
    parser.add_argument("--count", "-n", type=int, default=None,
                        help="Number of recent commits to include.")
    parser.add_argument("--compare-commits", nargs=2, metavar=('OLD', 'NEW'),
                        help="Compare between two commits or branches.")
    parser.add_argument("--last-pr", action="store_true",
                        help="Auto compare GITHUB_BASE_REF..GITHUB_HEAD_REF for GitHub Actions.")
    parser.add_argument("--mode", choices=["simple", "full"], default="simple",
                        help="Output mode: simple (clean) or full (with metadata).")
    parser.add_argument("--output-dir", default="output",
                        help="Directory to save output files.")
    parser.add_argument("--filename-template", default="diff_report_{first_hash}_to_{last_hash}",
                        help="Filename template. Use {count}, {first_hash}, {last_hash}.")
    return parser.parse_args()


def format_commit_diff(diff_text, mode, index):
    lines = diff_text.splitlines()
    show_metadata = mode == "simple"
    show_context = mode in ("simple", "full")

    output_lines = []
    meta_lines = []
    current_file = ""
    author_line = ""
    date_line = ""
    commit_message_lines = []
    commit_hash = ""

    parsing_commit_message = False

    for line in lines:
        if line.startswith("commit "):
            commit_hash = line.strip().split()[1]
            parsing_commit_message = False
            continue

        if line.startswith("Author:"):
            author_line = line.replace("Author:", "").strip()
            continue

        if line.startswith("Date:"):
            date_line = line.replace("Date:", "").strip()
            parsing_commit_message = True
            continue

        if parsing_commit_message:
            if line.strip() == "":
                continue
            if line.startswith("diff --git"):
                parsing_commit_message = False
            else:
                commit_message_lines.append(line.strip())
                continue

        if line.startswith("diff --git"):
            match = re.search(r'diff --git a/(.+?) b/\1', line)
            current_file = match.group(1) if match else line.split()[-1]
            output_lines.append(f"\n\n📝 <b>Змінено файл: {current_file}</b>")
            continue

        if show_metadata and (line.startswith("index ") or line.startswith("---") or line.startswith("+++")):
            continue

        if show_context and line.startswith("@@"):
            match = re.search(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', line)
            if match:
                start = int(match.group(1))
                length = int(match.group(2)) if match.group(2) else 1
                end = start + length - 1
                output_lines.append(f'<span style="color: blue;">🔧 Зміни в рядках {start}–{end}</span>')
            else:
                output_lines.append(f'<span style="color: blue;">🔧 Зміни в коді</span>')
            continue

        if line.startswith('+') and not line.startswith('+++'):
            output_lines.append(f'<span style="color: green;">{line}</span>')
        elif line.startswith('-') and not line.startswith('---'):
            output_lines.append(f'<span style="color: red;">{line}</span>')
        else:
            output_lines.append(line)

    # Метадані
    if show_metadata:
        meta_lines = ['<h2>🧾 Інформація про коміт</h2>']
        if author_line:
            meta_lines.append(f"<b>👤 Автор:</b> {author_line}")
        if date_line:
            meta_lines.append(f"<b>📅 Дата:</b> {date_line}")
        if commit_message_lines:
            message = " ".join(commit_message_lines)
            meta_lines.append(f"<b>💬 Повідомлення:</b> {message}")
        meta_lines.append("<hr style='border: 1px dashed gray;'>")

    content = "\n".join(meta_lines + output_lines)
    return content, commit_hash


def write_output(html_content, output_dir, filename_base):
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    html_path = output_dir / f"{filename_base}.html"
    pdf_path = output_dir / f"{filename_base}.pdf"

    html_full = (
            '<html><body><pre style="font-family: monospace; font-size: 12px;">'
            + html_content +
            '</pre></body></html>'
    )

    html_path.write_text(html_full, encoding="utf-8")
    HTML(string=html_full).write_pdf(pdf_path)

    print(f"✅ Збережено:\n  HTML: {html_path}\n  PDF: {pdf_path}")


def form_result(diff_output, mode, output_dir, filename_template , base_ref, head_ref):
    html_block, _ = format_commit_diff(diff_output, mode, 1)
    save_files(html_block, output_dir, filename_template, base_ref, head_ref)

def save_files(html_block, output_dir, filename_template, base_ref, head_ref, count=1):
    filename_base = filename_template.replace("{first_hash}", base_ref).replace("{last_hash}", head_ref).replace("{count}", str(count))
    write_output(html_block, output_dir, filename_base)
    
def process_last_pr(mode, output_dir, filename_template):
    base_ref = os.getenv("GITHUB_BASE_REF")
    head_ref = os.getenv("GITHUB_HEAD_REF")

    if not base_ref or not head_ref:
        print("❌ Не виявлено GITHUB_BASE_REF або GITHUB_HEAD_REF.")
        return

    subprocess.run(["git", "fetch", "origin", base_ref, head_ref], check=True)
    diff_output = subprocess.run(
        ["git", "diff", f"origin/{base_ref}", f"origin/{head_ref}"],
        capture_output=True,
        text=True
    ).stdout
    form_result(diff_output, mode, output_dir, filename_template, base_ref, head_ref)
    
def process_compare_commits(mode, output_dir, filename_template, old_ref, new_ref ):    
    diff_output = subprocess.run(
        ["git", "diff", f"{old_ref}", f"{new_ref}"],
        capture_output=True,
        text=True
    ).stdout
    form_result(diff_output, mode, output_dir, filename_template, old_ref, new_ref)

def form_last_n_commits(count):    
    command = ["git", "log", "-p", f"-n{count}"]
    git_log_output = subprocess.run(
        command,
        capture_output=True,
        text=True
    ).stdout    
    #print("RUN:", " ".join( command))
    #print(git_log_output)
    commits_raw = re.split(r'(?=^commit\s)', git_log_output, flags=re.MULTILINE)
    #print(commits_raw)
    return commits_raw

def main():
    args = parse_args()
    mode = args.mode
    output_dir = Path(args.output_dir)
    filename_template = args.filename_template
    
    # GitHub Actions режим
    if args.last_pr:
        process_last_pr(mode, output_dir, filename_template)
    # Порівняння двох гілок/комітів
    elif args.compare_commits:
        old_ref, new_ref = args.compare_commits
        process_compare_commits(mode, output_dir, filename_template, old_ref, new_ref)
    else:
        # Режим з останніми комітами
        count = args.count or 1
        commits_raw = form_last_n_commits(count)
        
        all_blocks = []
        hashes = []
        for idx, raw_commit in enumerate(commits_raw):
            if raw_commit:
                html_block, commit_hash = format_commit_diff(raw_commit, mode, idx + 1)
                all_blocks.append(html_block)
                hashes.append(commit_hash)
        html_content = "\n\n<hr style='border: 2px solid black;'>\n\n".join(all_blocks)
        first_hash = hashes[-1][:7] if hashes else "start"
        last_hash = hashes[0][:7] if hashes else "end"

        save_files(html_content, output_dir, filename_template, first_hash, last_hash, count)


if __name__ == "__main__":
    main()
