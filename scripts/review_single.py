"""review_single.py — Review a single file with OpenAI.

Usage:
    python scripts/review_single.py src/nexiss/services/ai/pipeline.py
    python scripts/review_single.py src/nexiss/api/v1/documents.py --model gpt-4o
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Re-use the review logic from auto_review
sys.path.insert(0, str(Path(__file__).parent))
from auto_review import review_file  # noqa: E402

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Review a single file with OpenAI")
    parser.add_argument("file", help="Path to the Python file to review")
    parser.add_argument("--model", default="gpt-4o", help="OpenAI model")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set.")
        sys.exit(1)

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)

    print(f"Reviewing {file_path} with {args.model}...\n")
    result = review_file(file_path, api_key, args.model)

    issues = result.get("issues", [])
    if issues:
        for issue in issues:
            severity = issue.get("severity", "info").upper()
            line = issue.get("line")
            msg = issue.get("message", "")
            loc = f" (line {line})" if line else ""
            print(f"[{severity}]{loc} {msg}")
    else:
        print("No issues found.")

    print(f"\nSummary: {result.get('summary', '')}")
    print(f"Approved: {result.get('approved', True)}")


if __name__ == "__main__":
    main()
