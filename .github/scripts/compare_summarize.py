import sys
import os
import subprocess
from transformers import T5ForConditionalGeneration, T5Tokenizer

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {cmd}\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def get_commit_messages(base, head, file_path):
    # Взяти коміти, які змінювали цей файл між base і head
    cmd = f'git log {base}..{head} --pretty=format:"%s" -- "{file_path}"'
    return run_cmd(cmd)

def get_diff(base, head, file_path):
    cmd = f'git diff {base} {head} -- "{file_path}"'
    return run_cmd(cmd)

def summarize_text(text, tokenizer, model):
    input_text = "summarize: " + text.replace("\n", " ")
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = model.generate(
        inputs,
        max_length=150,
        min_length=40,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def main():
    if len(sys.argv) != 4:
        print("Usage: python compare_summarize.py <base_commit> <head_commit> <comma_separated_md_files>")
        sys.exit(1)

    base = sys.argv[1]
    head = sys.argv[2]
    files = sys.argv[3].split(",")

    os.makedirs("summaries", exist_ok=True)

    print("Loading model...")
    model_name = "t5-small"
    tokenizer = T5Tokenizer.from_pretrained(model_name, legacy=False)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    for f in files:
        f = f.strip()
        if not f.endswith(".md"):
            print(f"Skipping non-md file: {f}")
            continue

        print(f"Processing file: {f}")

        # Отримуємо коміт-повідомлення
        commit_msgs = get_commit_messages(base, head, f)
        if not commit_msgs:
            commit_msgs = "(нема змін у повідомленнях комітів для цього файлу)"

        # Отримуємо diff
        diff_text = get_diff(base, head, f)
        if not diff_text:
            diff_text = "(нема змін у diff для цього файлу)"

        # Формуємо та записуємо резюме по commit messages
        print(commit_msgs)
        summary_commit = summarize_text(commit_msgs, tokenizer, model)
        print(summary_commit)
        with open(f"summaries/{os.path.basename(f)}_commit_summary.txt", "w", encoding="utf-8") as sf:
            sf.write(summary_commit)

        # Формуємо та записуємо резюме по diff
        print(diff_text)
        summary_diff = summarize_text(diff_text, tokenizer, model)
        print(summary_diff)
        with open(f"summaries/{os.path.basename(f)}_diff_summary.txt", "w", encoding="utf-8") as sf:
            sf.write(summary_diff)

        print(f"Summary for {f} done.")

if __name__ == "__main__":
    main()
