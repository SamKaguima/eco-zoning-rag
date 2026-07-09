"""PreToolUse hook (Bash matcher): blocks git commit/push until pytest passes.

Reads the PreToolUse hook payload on stdin, and if tool_input.command
contains a git commit or git push invocation, runs the project's test suite
first. The git command is denied if tests fail, allowed through if they pass.
Any other Bash command is allowed immediately without running tests.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYTEST_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

GIT_COMMIT_RE = re.compile(r"\bgit\s+commit\b")
GIT_PUSH_RE = re.compile(r"\bgit\s+push\b")


def emit(decision: str, reason: str = "") -> None:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
        }
    }
    if reason:
        output["hookSpecificOutput"]["permissionDecisionReason"] = reason
    print(json.dumps(output))
    sys.exit(0)


def main() -> None:
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")

    if not (GIT_COMMIT_RE.search(command) or GIT_PUSH_RE.search(command)):
        emit("allow")
        return

    if not PYTEST_PYTHON.exists():
        emit("allow", f"Test gate skipped: {PYTEST_PYTHON} not found.")
        return

    result = subprocess.run(
        [str(PYTEST_PYTHON), "-m", "pytest", "tests/", "-v"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        emit("allow")
        return

    tail = "\n".join((result.stdout + result.stderr).splitlines()[-25:])
    emit(
        "deny",
        "Test suite failed — git commit/push blocked until tests pass.\n\n"
        f"pytest exit code: {result.returncode}\n{tail}",
    )


if __name__ == "__main__":
    main()
