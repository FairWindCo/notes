import difflib
from git import Repo

def get_last_two_versions(repo_path, file_path):
    repo = Repo(repo_path)
    commits = list(repo.iter_commits(paths=file_path, max_count=2))

    if len(commits) < 2:
        raise Exception("Недостатньо комітів для порівняння.")

    old = (commits[1].tree / file_path).data_stream.read().decode('utf-8').splitlines()
    new = (commits[0].tree / file_path).data_stream.read().decode('utf-8').splitlines()
    return old, new

def describe_diff(old_lines, new_lines):
    diff = difflib.unified_diff(old_lines, new_lines, lineterm='')
    changes = []
    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            changes.append(f"➕ Додано: {line[1:]}")
        elif line.startswith('-') and not line.startswith('---'):
            changes.append(f"➖ Видалено: {line[1:]}")
    return '\n'.join(changes) if changes else "✅ Немає змін"

# ⚙️ Вкажіть шлях до вашого локального репозиторію і файлу
repo_path = '/шлях/до/репозиторію'  # Наприклад: './my-repo'
file_path = 'README.md'

old, new = get_last_two_versions(repo_path, file_path)
summary = describe_diff(old, new)
print("🔍 Опис змін у файлі:")
print(summary)
