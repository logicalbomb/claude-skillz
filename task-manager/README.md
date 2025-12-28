# Task Manager Skill for Claude Code

Manage personal tasks as GitHub Issues via Claude Code.

## Quick Install

```bash
export CSZ_TM_GITHUB_PAT="your_token"
curl -sfL https://raw.githubusercontent.com/logicalbomb/claude-skillz/main/task-manager/install-task-manager.sh | bash -s -- owner/repo
```

## Requirements

- [Claude Code](https://claude.ai/claude-code) CLI
- GitHub PAT with `repo` scope ([create one](https://github.com/settings/tokens))
- A GitHub repo to store tasks as issues

## Usage

After install, use natural language in Claude Code:

```
create task: Fix login bug, high priority
list my top 10 tasks
list my blockers
update task 7 due date to 2025-03-01
close task 3
```

## What It Installs

| File | Purpose |
|------|---------|
| `~/.claude/skills/task-manager/SKILL.md` | Skill definition |
| `~/.claude/hooks/validate-task-manager-curl.py` | Auto-approves safe GitHub API calls |
| `~/.claude/settings.json` | Adds skill permission + hook config |

## Installer Options

```
./install-task-manager.sh [OPTIONS] [owner/repo]

Options:
  --custom    Prompt for custom template/hook URLs
  --help      Show help
```

## Uninstall

```bash
curl -sfL https://raw.githubusercontent.com/logicalbomb/claude-skillz/main/task-manager/uninstall-task-manager.sh | bash
```
