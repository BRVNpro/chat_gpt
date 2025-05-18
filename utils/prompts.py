import os


def load_prompt(name: str) -> str:
    path = os.path.join("prompts", name)
    if not os.path.exists(path):
        return "⚠️ Промпт не найден."

    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_message(name: str) -> str:
    path = os.path.join("messages", name)
    if not os.path.exists(path):
        return "⚠️ Текст не найден."

    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()
