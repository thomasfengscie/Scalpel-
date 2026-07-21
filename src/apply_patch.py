#!/usr/bin/env python3
"""
Apply AI-suggested edits to files in-place.
Supports two input modes:
 - JSON range edits: a list of {path, start (1-based), end (1-based), text}
 - unified diff file: applied with `git apply`

This script is intentionally small and conservative: it prints diffs and can optionally create a git commit.
"""

import argparse
import json
import difflib
import subprocess
import sys
import os
from typing import List, Dict


def show_unified_diff(path: str, old_lines: List[str], new_lines: List[str]):
    diff = difflib.unified_diff(old_lines, new_lines, fromfile=path, tofile=path, lineterm="")
    print("\n".join(line for line in diff))

def apply_range_edits(edits: List[Dict], write: bool = True):
    made_changes = []
    for e in edits:
        path = e["path"]
        start = int(e["start"])  # 1-based inclusive
        end = int(e["end"])      # 1-based inclusive
        new_text = e["text"].splitlines(keepends=True)
        if not os.path.exists(path):
            print(f"ERROR: target file does not exist: {path}", file=sys.stderr)
            continue
        with open(path, "r", encoding="utf-8") as f:
            old_lines = f.readlines()
        s = max(0, start - 1)
        t = min(len(old_lines), end)
        new_lines = old_lines[:s] + new_text + old_lines[t:]
        show_unified_diff(path, old_lines, new_lines)
        if write:
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            made_changes.append(path)
    return made_changes

def apply_unified_diff(diff_text: str):
    # Use git apply for robustness where available. This must be run in a git repo.
    import tempfile
    with tempfile.NamedTemporaryFile("w", delete=False) as tf:
        tf.write(diff_text)
        tmpname = tf.name
    try:
        subprocess.check_call(["git", "apply", tmpname])
        print("Applied diff via git apply")
    except subprocess.CalledProcessError as exc:
        print("git apply failed:", exc, file=sys.stderr)
        return False
    finally:
        try:
            os.unlink(tmpname)
        except Exception:
            pass
    return True

def create_git_commit(message: str, paths: List[str]):
    try:
        subprocess.check_call(["git", "add"] + paths)
        subprocess.check_call(["git", "commit", "-m", message])
        print("Created git commit")
    except subprocess.CalledProcessError as exc:
        print("git commit failed:", exc, file=sys.stderr)

def main():
    p = argparse.ArgumentParser(description="Apply AI-suggested in-place edits")
    p.add_argument("--edits-json", help="path to JSON file with range edits")
    p.add_argument("--diff-file", help="path to unified diff file")
    p.add_argument("--no-write", action="store_true", help="print diffs but do not write")
    p.add_argument("--commit", action="store_true", help="create a git commit after applying edits")
    p.add_argument("--commit-msg", default="Apply AI edits", help="commit message")
    args = p.parse_args()

    written_paths = []
    if args.edits_json:
        with open(args.edits_json, "r", encoding="utf-8") as f:
            edits = json.load(f)
        written_paths = apply_range_edits(edits, write=(not args.no_write))
    elif args.diff_file:
        with open(args.diff_file, "r", encoding="utf-8") as f:
            diff_text = f.read()
        ok = apply_unified_diff(diff_text)
        if ok and not args.no_write:
            # find changed files via git diff --name-only
            try:
                out = subprocess.check_output(["git", "diff", "--name-only"]).decode().strip()
                written_paths = out.splitlines() if out else []
            except Exception:
                written_paths = []
    else:
        print("Provide --edits-json or --diff-file", file=sys.stderr)
        sys.exit(1)

    if args.commit and written_paths:
        create_git_commit(args.commit_msg, written_paths)


if __name__ == "__main__":
    main()
