"""
ai_driver.py

A tiny driver that shows how an AI's JSON response might be converted into a file and applied.
This is illustrative — real integrations call model APIs and validate outputs.
"""

import json
import subprocess
import sys


def run_example():
    # Example JSON edits (would normally come from an AI). This file is examples/ai_edits.json
    edits = [
        {
            "path": "examples/example_project/hello.py",
            "start": 1,
            "end": 3,
            "text": "def greet(name):\n    \"\"\"Return a friendly greeting.\"\"\"\n    return f\"Hello, {name}!\"\n"
        }
    ]
    with open("examples/ai_edits.json", "w", encoding="utf-8") as f:
        json.dump(edits, f, indent=2)
    # Call apply_patch.py to preview and apply
    subprocess.check_call([sys.executable, "src/apply_patch.py", "--edits-json", "examples/ai_edits.json"]) 


if __name__ == "__main__":
    run_example()
