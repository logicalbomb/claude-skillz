#!/usr/bin/env python3
import json
import re
import sys

ALLOWED_REPO = "__REPO__"

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    command = input_data.get("tool_input", {}).get("command", "")

    if tool_name != "Bash" or not command.strip().startswith("curl"):
        sys.exit(0)

    if not re.search(r"\bcurl\s+-s\b", command):
        deny("curl must use -s (silent) flag")

    if not re.search(rf"https://api\.github\.com/repos/{re.escape(ALLOWED_REPO)}", command):
        deny(f"Only api.github.com/repos/{ALLOWED_REPO} allowed")

    dangerous = [
        (r"--config|-K", "config files blocked"),
        (r"\||\\\$\(|\`", "pipes/subshells blocked"),
        (r">\s*\S+", "output redirection blocked"),
    ]
    for pattern, reason in dangerous:
        if re.search(pattern, command):
            deny(reason)

    allow("task-manager curl validated")

def allow(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": reason
        }
    }))
    sys.exit(0)

def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }))
    sys.exit(0)

if __name__ == "__main__":
    main()
