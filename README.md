Scalpel
Scalpel is a small demo/prototype showing how an AI assistant can make minimal, in-place edits to source code instead of rewriting entire files. The goal is to reduce token usage and make AI edits more reviewable and safe.

Contents:

README.md — this file
design.md — design notes and rationale
src/ — small tools to apply AI-suggested edits (range edits or unified diff)
examples/example_project — a tiny Python project with tests
examples/ai_suggested_patch.diff — sample unified diff produced by an AI
.github/workflows/ai-edit-ci.yml — CI that runs tests on PRs
docs/prompt_templates.md — prompt examples for requesting minimal edits from models
Quick start (after repository is cloned):

Apply JSON range edits (example): python3 src/apply_patch.py --edits-json examples/ai_edits.json

Apply a unified diff: python3 src/apply_patch.py --diff-file examples/ai_suggested_patch.diff

Design notes, usage, and prompt templates are in design.md and docs/.
