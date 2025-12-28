#!/bin/bash
set -e

#######################################
# CONFIGURATION
#######################################
DEFAULT_TEMPLATE_URL="https://raw.githubusercontent.com/logicalbomb/claude-skillz/main/task-manager/SKILL.template.md"
DEFAULT_HOOK_URL="https://raw.githubusercontent.com/logicalbomb/claude-skillz/main/task-manager/validate-task-manager-curl.template.py"

#######################################
# HELP
#######################################
show_help() {
    cat << EOF
Task Manager Skill Installer for Claude Code

Usage: ./install-task-manager.sh [OPTIONS] [owner/repo]

Options:
  --custom    Prompt for custom template/hook URLs
  --help      Show this help message

Examples:
  ./install-task-manager.sh myuser/my-tasks
  ./install-task-manager.sh --custom myuser/my-tasks
  curl -sfL <installer-url> | bash -s -- myuser/my-tasks

Environment:
  CSZ_TM_GITHUB_PAT  Required. GitHub PAT with 'repo' scope.

EOF
    exit 0
}

#######################################
# PARSE ARGS
#######################################
CUSTOM_MODE=false
REPO=""

for arg in "$@"; do
    case $arg in
        --help|-h)
            show_help
            ;;
        --custom)
            CUSTOM_MODE=true
            ;;
        *)
            if [[ -z "$REPO" ]]; then
                REPO="$arg"
            fi
            ;;
    esac
done

#######################################
# GATHER INPUTS
#######################################
TEMPLATE_URL="${DEFAULT_TEMPLATE_URL}"
HOOK_URL="${DEFAULT_HOOK_URL}"

if [[ -z "$REPO" ]]; then
    read -p "Enter GitHub repo for tasks (owner/repo): " REPO
    if [[ -z "$REPO" ]]; then
        echo "Error: Repo is required"
        exit 1
    fi
fi

if [[ ! "$REPO" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$ ]]; then
    echo "Error: Invalid repo format. Use owner/repo"
    exit 1
fi

if [[ "$CUSTOM_MODE" == true ]]; then
    read -p "Template URL [$DEFAULT_TEMPLATE_URL]: " INPUT_URL
    if [[ -n "$INPUT_URL" ]]; then
        TEMPLATE_URL="$INPUT_URL"
    fi

    read -p "Hook URL [$DEFAULT_HOOK_URL]: " INPUT_HOOK_URL
    if [[ -n "$INPUT_HOOK_URL" ]]; then
        HOOK_URL="$INPUT_HOOK_URL"
    fi
fi

if [[ -z "$CSZ_TM_GITHUB_PAT" ]]; then
    echo "Error: CSZ_TM_GITHUB_PAT environment variable not set"
    echo "Create a PAT with 'repo' scope at: https://github.com/settings/tokens"
    exit 1
fi

#######################################
# VALIDATE PAT
#######################################
echo "Validating GitHub PAT..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $CSZ_TM_GITHUB_PAT" "https://api.github.com/repos/$REPO")
if [[ "$HTTP_STATUS" != "200" ]]; then
    echo "Error: Cannot access $REPO (HTTP $HTTP_STATUS)"
    echo "Check that CSZ_TM_GITHUB_PAT has 'repo' scope and the repo exists."
    exit 1
fi
echo "PAT validated."

#######################################
# FETCH TEMPLATES
#######################################
echo "Fetching skill template..."
TEMPLATE_CONTENT=$(curl -sfL "$TEMPLATE_URL")
if [[ -z "$TEMPLATE_CONTENT" ]]; then
    echo "Error: Failed to fetch template from $TEMPLATE_URL"
    exit 1
fi

echo "Fetching hook template..."
HOOK_CONTENT=$(curl -sfL "$HOOK_URL")
if [[ -z "$HOOK_CONTENT" ]]; then
    echo "Error: Failed to fetch hook from $HOOK_URL"
    exit 1
fi

#######################################
# INSTALL
#######################################
echo "Installing task-manager skill for $REPO..."

# Create directories
mkdir -p ~/.claude/skills/task-manager
mkdir -p ~/.claude/hooks

# Substitute and write SKILL.md
echo "$TEMPLATE_CONTENT" | sed "s|__REPO__|$REPO|g" > ~/.claude/skills/task-manager/SKILL.md

# Substitute and write hook
echo "$HOOK_CONTENT" | sed "s|__REPO__|$REPO|g" > ~/.claude/hooks/validate-task-manager-curl.py
chmod +x ~/.claude/hooks/validate-task-manager-curl.py

# Merge settings.json
python3 << 'PYEOF'
import json
import os

settings_path = os.path.expanduser("~/.claude/settings.json")

if os.path.exists(settings_path):
    with open(settings_path) as f:
        settings = json.load(f)
else:
    settings = {}

settings.setdefault("permissions", {})
settings["permissions"].setdefault("allow", [])
settings.setdefault("hooks", {})
settings["hooks"].setdefault("PreToolUse", [])

perm = "Skill(task-manager)"
if perm not in settings["permissions"]["allow"]:
    settings["permissions"]["allow"].append(perm)

hook_entry = {
    "matcher": "Bash",
    "hooks": [{
        "type": "command",
        "command": "~/.claude/hooks/validate-task-manager-curl.py"
    }]
}

hook_exists = any(
    h.get("matcher") == "Bash" and
    any(hh.get("command", "").endswith("validate-task-manager-curl.py")
        for hh in h.get("hooks", []))
    for h in settings["hooks"]["PreToolUse"]
)

if not hook_exists:
    settings["hooks"]["PreToolUse"].append(hook_entry)

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
PYEOF

echo ""
echo "Done! Installed:"
echo "  ~/.claude/skills/task-manager/SKILL.md"
echo "  ~/.claude/hooks/validate-task-manager-curl.py"
echo "  ~/.claude/settings.json (merged)"
echo ""
echo "Restart Claude Code to activate."
