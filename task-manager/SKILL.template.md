# Task Manager

Manage personal tasks as GitHub Issues with structured metadata and tags for skill coordination.

## Prerequisites Check (REQUIRED)

Before ANY task operation, verify the PAT exists:

```bash
printenv CSZ_TM_GITHUB_PAT | head -c 10
```

If empty or command fails, STOP and tell user:
> "CSZ_TM_GITHUB_PAT environment variable not set. Add `export CSZ_TM_GITHUB_PAT=your_token` to your shell profile (~/.zshrc or ~/.bashrc) and restart your terminal."

Do NOT proceed with any curl commands until PAT is confirmed.

## Curl Command Format (CRITICAL)

**Permission patterns use prefix matching.** Commands MUST follow this exact format to avoid permission prompts:

```bash
# GET requests
curl -s -H "Authorization: token $PAT" "https://api.github.com/..."

# POST requests
curl -s -X POST -H "Authorization: token $PAT" https://api.github.com/... -d '...'

# PATCH requests
curl -s -X PATCH -H "Authorization: token $PAT" https://api.github.com/... -d '...'
```

**Rules:**
- Always use `-s` (silent) immediately after `curl`
- Authorization header MUST be the first `-H` flag
- Do NOT add `-H "Content-Type: application/json"` (GitHub API infers it)
- No extra flags between `-X METHOD` and `-H "Authorization..."`

## Quick Start

**Prerequisites**: GitHub PAT with `repo` scope, dedicated tasks repository

**Creating a task**:
```bash
curl -s -X POST -H "Authorization: token $CSZ_TM_GITHUB_PAT" \
  https://api.github.com/repos/{owner}/{repo}/issues \
  -d '{"title": "Task title", "body": "---\nPriority: High\n---\n\nDescription", "labels": ["READ"]}'
```

## Task Data Model

Each task is a GitHub Issue with:

**GitHub Native Fields**:
- Title: Issue title (max 180 chars, required)
- Body: Issue description with YAML frontmatter + markdown
- Labels: Tags for categorization and skill routing
- State: `open` or `closed`
- Number: Auto-assigned ID/slug for references
- created_at/updated_at: Automatic timestamps
- Comments: Updates from agents and user

**Frontmatter Fields** (YAML in issue body):
```yaml
---
Priority: High|Moderate|Low  # Default: Moderate
URL: https://example.com     # Optional link to work area
Dependencies: #123, #456     # Optional task IDs that must complete first
DueDate: 2025-01-15         # Optional ISO date
---

Markdown description and context for task details...
```

## Common Operations

### Create Task
```bash
curl -s -X POST -H "Authorization: token $CSZ_TM_GITHUB_PAT" \
  https://api.github.com/repos/__REPO__/issues \
  -d '{"title": "Task title", "body": "---\nPriority: Moderate\n---\n\nDescription"}'
```

### Update Task
```bash
# Add comment
curl -s -X POST -H "Authorization: token $CSZ_TM_GITHUB_PAT" \
  https://api.github.com/repos/__REPO__/issues/NUMBER/comments \
  -d '{"body": "Progress update..."}'

# Close task
curl -s -X PATCH -H "Authorization: token $CSZ_TM_GITHUB_PAT" \
  https://api.github.com/repos/__REPO__/issues/NUMBER \
  -d '{"state": "closed"}'
```

### Query Tasks
```bash
# Open tasks
curl -s -H "Authorization: token $CSZ_TM_GITHUB_PAT" \
  "https://api.github.com/repos/__REPO__/issues?state=open&per_page=10"

# Filter by label
curl -s -H "Authorization: token $CSZ_TM_GITHUB_PAT" \
  "https://api.github.com/repos/__REPO__/issues?labels=READ&state=open"
```

## Querying Blockers

When user asks for "blockers" or "dependencies", show **blocking tasks** (tasks that block others).

**Query open tasks** (`state=open`), exclude deferred. Open, blocked, and in-progress tasks can all have blockers.

**Output format** - blocker first, then what it blocks:
```
#7 Replace back part of roof
  → blocks #8 Repair ceiling drywall
```

Parse open tasks (excluding deferred), extract `Dependencies:` from frontmatter, invert to show blockers.

## Tag Vocabulary

**Core action tags**:
- **READ**: Review, analyze, summarize, research content
- **SCHEDULE**: Calendar events, meetings, time blocking
- **MESSAGE**: Send emails, Slack messages, notifications
- **DEFINE**: Write, create, draft content/code/specs
- **AUTHORIZE**: Requires user approval or decision
