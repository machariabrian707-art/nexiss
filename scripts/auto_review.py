import os
import time
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from openai import OpenAI

# Load config
CONFIG_PATH = Path("scripts/review_config.json")
with open(CONFIG_PATH, "r") as f:
    CFG = json.load(f)

# OpenAI setup
client = OpenAI(api_key=os.getenv("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"))

INCLUDE_EXT = tuple(CFG["include_extensions"])
IGNORE_DIRS = set(CFG["ignore_dirs"])
MAX_CHARS = CFG["max_chars"]

def should_ignore(path):
    return any(part in IGNORE_DIRS for part in path.parts)

def read_file(path):
    try:
        return path.read_text()[:MAX_CHARS]
    except:
        return "Error reading file"

def review_code(file_path):
    code = read_file(file_path)

    prompt = f"""
{CFG['review_prompt']}

FILE: {file_path}

CODE:
{code}
"""

    try:
        response = client.chat.completions.create(
            model=CFG["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=CFG["temperature"],
        )

        output = response.choices[0].message.content

        print("\n" + "="*80)
        print(f"REVIEWING: {file_path}")
        print("="*80)
        print(output)
        print("="*80 + "\n")

    except Exception as e:
        print("OpenAI Error:", e)


class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)

        if should_ignore(path):
            return

        if path.suffix in INCLUDE_EXT:
            review_code(path)


if __name__ == "__main__":
    observer = Observer()
    observer.schedule(Handler(), ".", recursive=True)
    observer.start()

    print("AI Overseer running...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()