# Prompt Template: Generating JSON Range Edits for AI-driven Patching

This document explains a recommended prompt template and constraints for instructing an LLM to produce "range edit" JSON objects that can be consumed by tooling (for example, scripts/apply_ai_edits.py).

Summary
- Output MUST be a single JSON array (only JSON, no surrounding explanation).
- Each array item is an object with: path, start (1-based), end (1-based inclusive), text.
- `text` must be a JSON string. Use `\n` for newlines (i.e., valid JSON escapes).
- The consumer expects 1-based inclusive line ranges.

System prompt (recommended)
You are a code-edit assistant that outputs machine-readable JSON only. Given a repository and an edit request, produce a JSON array where each element is an object with:
- "path": relative path to the file to create or edit
- "start": 1-based inclusive start line number
- "end": 1-based inclusive end line number
- "text": replacement text as a JSON string (use `\n` for newlines)
Output ONLY the JSON array. Do NOT return any explanatory text, Markdown, or code fences. Validate that your ranges are consistent with the repository context; if the file does not exist, create an edit for the new file with start=1 and end=0 (or state it in metadata if the system allows). Use minimal edits (replace only the necessary lines).

User prompt (example, English)
Please update the repository according to the request below. Return only a JSON array of edit objects.

Repository context (examples):
- examples/example_project/hello.py currently contains a greeting function.

Request:
- Make the greeting function return "Hi, {name}!" instead of "Hello, {name}!".
- Keep docstring and formatting similar.

Return:
- A JSON array where each item has path, start, end, text. Use 1-based inclusive line numbers. Output only the JSON array.

User prompt (example, Chinese)
请根据以下请求修改仓库中的文件。仅返回包含编辑项的 JSON 数组。

仓库上下文示例：
- examples/example_project/hello.py 包含一个问候函数。

请求：
- 将问候函数的返回值从 "Hello, {name}!" 改为 "Hi, {name}!"，保留 docstring 和格式。

返回格式：
- JSON 数组，每项包含 path、start、end、text（行号为从1开始，end 包含）。仅输出 JSON 数组。

Example output (valid)
[
  {
    "path": "examples/example_project/hello.py",
    "start": 1,
    "end": 3,
    "text": "def greet(name):\\n    \"\"\"Return a friendly greeting.\"\"\"\\n    return f\"Hi, {name}!\"\\n"
  }
]

Best practices and constraints
- Always return valid JSON (no trailing commas).
- Use 1-based inclusive line ranges. If the file will be created, prefer start=1,end=0 and put the full file content in `text`.
- Escape newlines as `\n` inside the JSON string. Do not output raw multiline strings that break JSON.
- Keep edits minimal: prefer replacing only the exact lines that need change.
- Do not include comments or notes in the JSON output.
- If unsure about line numbers, prefer returning an edit that sets the entire file content (start=1,end=<current_line_count>) or create the file if it doesn't exist.
- If multiple independent changes are required across files, include multiple array items.
- When in doubt, include a single edit per file.

Verification checklist (what humans/CI should check)
1. The PR / CI validates that the output is valid JSON (parseable).
2. For each edit where the file exists:
   - Check that start>=1 and end<=number_of_lines and start<=end.
3. For new files: ensure the `text` content is correct and start=1,end=0 (or other project convention).
4. Run a linter/tests to ensure changes don't break behavior.
5. If automated apply is used, run in --check/dry-run mode first.
6. Confirm the model did not include explanatory text outside the JSON (CI can fail on this).

Negative examples (what to avoid)
- Do NOT output:
  ```json
  // Here is the edit:
  [ {...} ]
  ```
  or Markdown/code fences. CI will reject anything that is not strictly JSON.

- Do NOT mix explanation with JSON. Return the JSON array only.

Notes about safety and review
- Treat any automated edit as a proposal: always run tests and review before merging.
- Prefer PR-based workflow to let CI and reviewers inspect AI-proposed edits.

If you want, I can:
- produce a ready-to-paste system + user prompt pair for a specific model (GPT-4o / ChatGPT-like),
- or add a small GH Action that rejects PRs with non-JSON model outputs (we can implement a PR check that ensures commit/PR body contains only valid JSON in a specific path).
