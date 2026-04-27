"""auto_review.py — Nexiss automated code review runner.

Scans recently changed Python files in the repo and asks OpenAI
to review them against the Nexiss coding standards.

Usage (from repo root):
    python scripts/auto_review.py [--path src/nexiss] [--model gpt-4o]

Requires:
    OPENAI_API_KEY environment variable (or in .env file)
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import json
from pathlib import Path

try:
    import httpx
except ImportError:
    print("httpx not installed. Run: pip install httpx")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional


NEXISS_REVIEW_SYSTEM_PROMPT = """
You are a senior backend engineer reviewing code for the Nexiss Document Intelligence SaaS platform.

Nexiss is a multi-tenant FastAPI + PostgreSQL + Celery system that:
- Accepts document uploads (images, PDFs, scans)
- Runs OCR + LLM extraction to turn them into structured data
- Classifies documents into ~50 types (invoices, medical records, contracts, etc.)
- Links entities (patient names, vendor names) across documents
- Exports to CSV/XLSX spreadsheets
- Provides analytics and an admin dashboard

When reviewing, check for:
1. Multi-tenancy violations (any query missing org_id scoping = critical bug)
2. Missing async/await on database calls
3. Unhandled exceptions that could crash a Celery worker
4. Hard-coded credentials or secrets
5. Missing input validation
6. Logic that could cause wrong document type to be used for extraction
7. Performance issues (N+1 queries, missing indexes)
8. Any code that exposes automation internals to users (they must never see it)

Format your response as JSON:
{
  "issues": [
    {"severity": "critical|high|medium|low", "line": <int or null>, "message": "<text>"}
  ],
  "summary": "<one paragraph overall assessment>",
  "approved": <true|false>
}
"""


def get_changed_files(path: str) -> list[Path]:
    """Get list of Python files changed vs main branch."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True, check=True
        )
        changed = [
            Path(f) for f in result.stdout.splitlines()
            if f.endswith(".py") and f.startswith(path.lstrip("/"))
        ]
        return [f for f in changed if f.exists()]
    except subprocess.CalledProcessError:
        # Fallback: scan all .py files in path
        return list(Path(path).rglob("*.py"))


def review_file(file_path: Path, api_key: str, model: str) -> dict:
    """Send file content to OpenAI for review."""
    content = file_path.read_text(encoding="utf-8")
    if not content.strip():
        return {"issues": [], "summary": "Empty file — skipped.", "approved": True}

    messages = [
        {"role": "system", "content": NEXISS_REVIEW_SYSTEM_PROMPT},
        {"role": "user", "content": f"Review this file: {file_path}\n\n```python\n{content}\n```"},
    ]

    with httpx.Client(timeout=60) as client:
        resp = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": messages,
                "response_format": {"type": "json_object"},
            },
        )
        resp.raise_for_status()
        body = resp.json()

    raw = body["choices"][0]["message"]["content"]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"issues": [], "summary": raw, "approved": False}


def main() -> None:
    parser = argparse.ArgumentParser(description="Nexiss automated code review")
    parser.add_argument("--path", default="src/nexiss", help="Path to scan (default: src/nexiss)")
    parser.add_argument("--model", default="gpt-4o", help="OpenAI model (default: gpt-4o)")
    parser.add_argument("--all", action="store_true", help="Review ALL .py files, not just changed ones")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set. Add it to .env or export it.")
        sys.exit(1)

    if args.all:
        files = list(Path(args.path).rglob("*.py"))
    else:
        files = get_changed_files(args.path)

    if not files:
        print("No Python files to review.")
        return

    print(f"Reviewing {len(files)} file(s) with {args.model}...\n")
    any_critical = False

    for f in files:
        print(f"--- {f} ---")
        result = review_file(f, api_key, args.model)
        issues = result.get("issues", [])
        approved = result.get("approved", True)
        summary = result.get("summary", "")

        for issue in issues:
            severity = issue.get("severity", "info").upper()
            line = issue.get("line")
            msg = issue.get("message", "")
            loc = f" (line {line})" if line else ""
            print(f"  [{severity}]{loc} {msg}")
            if severity == "CRITICAL":
                any_critical = True

        print(f"  Summary: {summary}")
        print(f"  Approved: {approved}\n")

    if any_critical:
        print("CRITICAL issues found. Please fix before merging.")
        sys.exit(1)
    else:
        print("Review complete. No critical issues.")


if __name__ == "__main__":
    main()
