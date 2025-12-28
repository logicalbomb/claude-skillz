#!/bin/bash
set -e

echo "Uninstalling task-manager skill..."

# Remove skill directory
rm -rf ~/.claude/skills/task-manager
echo "  Removed ~/.claude/skills/task-manager/"

# Remove hook script
rm -f ~/.claude/hooks/validate-task-manager-curl.py
echo "  Removed ~/.claude/hooks/validate-task-manager-curl.py"

# Clean settings.json
if [[ -f ~/.claude/settings.json ]]; then
    python3 << 'PYEOF'
import json
import os

settings_path = os.path.expanduser("~/.claude/settings.json")

with open(settings_path) as f:
    settings = json.load(f)

# Remove permission
perms = settings.get("permissions", {}).get("allow", [])
settings["permissions"]["allow"] = [p for p in perms if p != "Skill(task-manager)"]

# Remove hook
hooks = settings.get("hooks", {}).get("PreToolUse", [])
settings["hooks"]["PreToolUse"] = [
    h for h in hooks
    if not any(
        hh.get("command", "").endswith("validate-task-manager-curl.py")
        for hh in h.get("hooks", [])
    )
]

# Clean up empty structures
if not settings["permissions"]["allow"]:
    del settings["permissions"]["allow"]
if not settings["permissions"]:
    del settings["permissions"]
if not settings["hooks"]["PreToolUse"]:
    del settings["hooks"]["PreToolUse"]
if not settings["hooks"]:
    del settings["hooks"]

if settings:
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
    print("  Cleaned ~/.claude/settings.json")
else:
    os.remove(settings_path)
    print("  Removed empty ~/.claude/settings.json")
PYEOF
fi

echo "Done! Restart Claude Code to complete."
