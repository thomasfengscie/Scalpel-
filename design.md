Scalpel — design notes

Goals
- Encourage AI to produce minimal edits to existing code (line-range edits, AST edits, or unified diffs).
- Make edits auditable and testable.
- Integrate into a typical Git PR workflow.

Key ideas
- Prefer structured edits: JSON objects with path, start_line, end_line, replacement_text.
- Fallback: unified diff (git apply compatible).
- Validate patches by running tests and linters in CI; if checks fail, revert or run iterative repair cycles.

Security & safety
- Require machine-readable patch formats to prevent extraneous commentary.
- Run patches in ephemeral CI runners; do not auto-merge without human approval.
- Provide easy rollback (git revert or branch discard).

AI prompting
- Prompt the model to output only JSON or raw unified diff, nothing else.
- Provide the file content context (or limited chunk) and ask for minimal edits only.

Example flow
1. User reports bug.
2. AI proposes edits as JSON range edits.
3. apply_patch.py applies edits locally and prints a unified diff.
4. Agent/CI runs tests. If green, create PR with the changes. Human reviews and merges.
