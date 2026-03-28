# ADR Author Skill Adaptation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Adapt the domain-specific ADR author skill into a project-agnostic skill conforming to tasty-dev's architecture, making it the sole way to create and review ADRs.

**Architecture:** The skill resolves project root by finding `.tasty-dev/config.yaml` (bootstrapping via `init-project-storage` if missing). All ADR operations target `PROJECT_ROOT/.tasty-dev/adr/`. Examples are context-aware: generic when no ADRs exist, derived from existing ADRs otherwise. CLI tools are removed — the skill owns the full ADR lifecycle.

**Tech Stack:** Claude Code skill (markdown), Python (tests, init script), YAML (MADR frontmatter, config)

**Design doc:** `docs/plans/2026-03-27-adr-author-skill-adaptation-design.md`

---

### Task 1: Upgrade MADR Template

**Files:**
- Modify: `templates/adr-template.md`

**Step 1: Replace template content with MADR format**

Replace the entire contents of `templates/adr-template.md` with:

```markdown
---
status: draft
date: {date}
decision-makers: []
consulted: []
informed: []
domains: []
affects: []
related: []
supersedes: []
enforces: []
discussion:
  participants: []
  unread_by: []
  started: {date}
  last_updated: {date}
---

# {title}

## Context and Problem Statement

{problem description}

## Decision Drivers

* {driver 1}

## Considered Options

* Option 1: {name}
* Option 2: {name}

## Decision Outcome

Chosen option: "{option}", because {justification}.

### Consequences

* Good, because {positive consequence}
* Bad, because {negative consequence}

## Pros and Cons of the Options

### Option 1: {name}

{description}

* Good, because {pro}
* Bad, because {con}

## Discussion

## More Information
```

**Step 2: Verify template has valid YAML frontmatter**

Run: `python3 -c "import yaml; f=open('templates/adr-template.md'); lines=f.read().split('---'); yaml.safe_load(lines[1]); print('Valid YAML')"`
Expected: `Valid YAML`

**Step 3: Commit**

```
feat(adr): upgrade template to MADR format with YAML frontmatter
```

---

### Task 2: Rewrite Tests for Template and Init Validation

**Files:**
- Modify: `tests/test_adr_creation.py`

**Step 1: Write test for MADR template YAML validity**

Replace the contents of `tests/test_adr_creation.py` with:

```python
# tests/test_adr_creation.py
"""Tests for ADR infrastructure: init-project-storage and MADR template."""
import subprocess
import tempfile
from pathlib import Path

import yaml


TEMPLATE_PATH = Path("templates/adr-template.md")


def _parse_frontmatter(content: str) -> dict:
    """Extract and parse YAML frontmatter from markdown content."""
    parts = content.split("---", 2)
    assert len(parts) >= 3, "Template must have YAML frontmatter between --- delimiters"
    return yaml.safe_load(parts[1])


def test_template_has_valid_yaml_frontmatter():
    """MADR template contains parseable YAML frontmatter."""
    content = TEMPLATE_PATH.read_text()
    frontmatter = _parse_frontmatter(content)
    assert isinstance(frontmatter, dict)


def test_template_has_required_frontmatter_fields():
    """MADR template includes all required metadata fields."""
    content = TEMPLATE_PATH.read_text()
    frontmatter = _parse_frontmatter(content)

    required_fields = [
        "status", "date", "decision-makers", "consulted", "informed",
        "domains", "affects", "related", "supersedes", "enforces",
        "discussion",
    ]
    for field in required_fields:
        assert field in frontmatter, f"Missing required field: {field}"


def test_template_has_discussion_metadata():
    """MADR template discussion block has participant tracking fields."""
    content = TEMPLATE_PATH.read_text()
    frontmatter = _parse_frontmatter(content)
    discussion = frontmatter["discussion"]

    assert "participants" in discussion
    assert "unread_by" in discussion
    assert "started" in discussion
    assert "last_updated" in discussion


def test_template_has_required_sections():
    """MADR template has all required markdown sections."""
    content = TEMPLATE_PATH.read_text()

    required_sections = [
        "## Context and Problem Statement",
        "## Decision Drivers",
        "## Considered Options",
        "## Decision Outcome",
        "### Consequences",
        "## Pros and Cons of the Options",
        "## Discussion",
        "## More Information",
    ]
    for section in required_sections:
        assert section in content, f"Missing required section: {section}"


def test_init_project_storage_creates_adr_directory():
    """init-project-storage creates .tasty-dev/adr/ directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        result = subprocess.run(
            ["bin/init-project-storage", str(project_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert (project_path / ".tasty-dev" / "adr").is_dir()


def test_init_project_storage_creates_config():
    """init-project-storage creates config.yaml with expected fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(
            ["bin/init-project-storage", str(project_path)],
            capture_output=True,
        )

        config_path = project_path / ".tasty-dev" / "config.yaml"
        assert config_path.exists()

        config = yaml.safe_load(config_path.read_text())
        assert "knowledge_repo" in config
        assert "last_project_review" in config
        assert "last_knowledge_review" in config


def test_init_project_storage_is_idempotent():
    """Running init-project-storage twice does not overwrite config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # First run
        subprocess.run(
            ["bin/init-project-storage", str(project_path)],
            capture_output=True,
        )

        # Modify config to prove it isn't overwritten
        config_path = project_path / ".tasty-dev" / "config.yaml"
        config = yaml.safe_load(config_path.read_text())
        config["knowledge_repo"] = "/some/path"
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        # Second run
        subprocess.run(
            ["bin/init-project-storage", str(project_path)],
            capture_output=True,
        )

        # Config should retain modification
        config = yaml.safe_load(config_path.read_text())
        assert config["knowledge_repo"] == "/some/path"
```

**Step 2: Run tests to verify they pass**

Run: `cd /Users/zac.propersi/projects/github/claude-skillz/tasty-dev && python3 -m pytest tests/test_adr_creation.py -v`
Expected: All 7 tests PASS (template tests pass against the upgraded template from Task 1)

**Step 3: Commit**

```
test(adr): rewrite tests for MADR template and init-project-storage
```

---

### Task 3: Remove CLI Tools and Old Tests

**Files:**
- Delete: `bin/create-adr`
- Delete: `bin/query-adr`
- Delete: `tests/test_adr_query.py`

**Step 1: Delete the three files**

Remove `bin/create-adr`, `bin/query-adr`, and `tests/test_adr_query.py`.

**Step 2: Verify remaining tests still pass**

Run: `cd /Users/zac.propersi/projects/github/claude-skillz/tasty-dev && python3 -m pytest tests/ -v`
Expected: All tests from `test_adr_creation.py` pass. No import errors or broken references.

**Step 3: Commit**

```
refactor(adr): remove CLI tools, skill owns ADR lifecycle
```

---

### Task 4: Update project-weekly Review Skill

The project-weekly review skill at `skills/reviews/project-weekly.md:34-37` references `bin/create-adr`. Update it to reference the adr-author skill instead.

**Files:**
- Modify: `skills/reviews/project-weekly.md`

**Step 1: Replace the bin/create-adr reference in Step 2**

In `skills/reviews/project-weekly.md`, replace:

```markdown
For strategic items:

```bash
bin/create-adr . "Title from reflexion"
```

Fill in the ADR with:
- Context from reflexion
- Decision (resolution)
- Alternatives considered
- Consequences
```

With:

```markdown
For strategic items, hand off to the ADR author skill:

Invoke `/adr-author` with the reflexion context pre-loaded. The skill's guided conversation will capture the decision with full context, alternatives, and consequences through its 9-step workflow.
```

**Step 2: Commit**

```
refactor(reviews): reference adr-author skill instead of removed CLI tool
```

---

### Task 5: Register adr-author in SKILL.md

**Files:**
- Modify: `SKILL.md`

**Step 1: Add adr-author command to SKILL.md**

In `SKILL.md`, after the `correct` command section (around line 36), add:

```markdown
### `adr-author`
Create or review architecture decision records through guided conversation.

**Trigger**: Use when making architectural decisions, reviewing existing ADRs, or when a reflexion capture escalates to a strategic decision.

**Skill**: `adr/skill`

**Modes**:
- `/adr-author` — Create a new ADR
- `/adr-author --review` — Review all unread ADRs
- `/adr-author --review <file>` — Review a specific ADR
```

**Step 2: Commit**

```
feat(adr): register adr-author command in SKILL.md
```

---

### Task 6: Rewrite Skill — Header, Purpose, Usage, and Bash Interpretation

This task and Tasks 7-13 collectively rewrite `skills/adr/skill.md`. Each task handles a logical section of the skill.

**Files:**
- Modify: `skills/adr/skill.md`

**Step 1: Replace the frontmatter and everything through "Interpreting Bash Code Blocks" section (lines 1-63)**

Replace lines 1 through the end of the "Interpreting Bash Code Blocks" section with:

```markdown
---
name: adr-author
description: Guide creation and review of architecture decision records through conversational workflow
---

# ADR Author Skill

## Purpose

This skill guides the creation and review of Architecture Decision Records (ADRs) through a structured conversational workflow. It:

- Facilitates thoughtful decision-making through guided questions
- Suggests options based on existing ADRs and project context
- Provides skeptical review to challenge decisions before finalization
- Ensures consistency with existing architectural decisions
- Manages asynchronous discussion, review, and approval workflows

## Usage

Invoke this skill in four ways:

```bash
# Create a new ADR
/adr-author

# Review all ADRs needing your attention
/adr-author --review

# Review and discuss specific ADR
/adr-author --review .tasty-dev/adr/0015-some-decision.md
```

**Behavioral modes:**

- **Creation mode** (`/adr-author`): 9-step guided workflow to create new ADR
- **Review all mode** (`/adr-author --review`): Find and review all unread ADRs sequentially
- **Review specific mode** (`/adr-author --review <file>`): Review and discuss one ADR

## Project Root Resolution

Before any ADR operation, resolve the project root:

1. Walk up from the current working directory or run `git rev-parse --show-toplevel` to find a `.tasty-dev/` directory containing `config.yaml`
2. If found: that directory's parent is `PROJECT_ROOT`. All ADR operations use `PROJECT_ROOT/.tasty-dev/adr/`
3. If not found: ask the user if they'd like to initialize tasty-dev storage, then run `bin/init-project-storage PROJECT_ROOT`
4. Cache `PROJECT_ROOT` for the remainder of the session

## Interpreting Bash Code Blocks

Throughout this skill, bash code blocks serve different purposes:

**Commands Claude should execute:**
- Git operations: `git log`, `git status`, `git diff`, `git show`, `git config`
- These commands gather information about the repository state
- Execute these directly using the Bash tool

**Illustrative examples:**
- Examples showing command syntax or patterns (e.g., invocation examples: `/adr-author`, `/adr-author --review`)
- Examples in user conversation flows (e.g., showing what user types)
- These are for documentation purposes only; do not execute

**File operations:**
- References like `cat /path/to/file.md` or `tail -20 /path/to/file.md`
- These indicate Claude should use the Read tool instead of bash commands
- Per CLAUDE.md: Never use `cat`, `tail`, `head`, or similar bash commands for reading files
- Always use the Read tool for file content operations

**When in doubt:** If a bash block is describing what to show users or appears in example conversations, it's illustrative. If it's in a process step telling Claude what to do, execute it (unless it's a file operation, in which case use Read tool).
```

**Step 2: Verify the file still parses as valid markdown with frontmatter**

Run: `python3 -c "f=open('skills/adr/skill.md'); content=f.read(); parts=content.split('---', 2); print('Frontmatter OK' if len(parts) >= 3 else 'BROKEN')"`
Expected: `Frontmatter OK`

---

### Task 7: Rewrite Skill — Step 1 (Initialize Context)

**Files:**
- Modify: `skills/adr/skill.md`

**Step 1: Replace Step 1 section**

Replace the entire "### Step 1: Initialize Context" section (original lines 69-131) with:

```markdown
### Step 1: Initialize Context

**Resolve project root** (see Project Root Resolution above).

**Determine next ADR number:**
- Read `PROJECT_ROOT/.tasty-dev/adr/` to find highest numbered ADR file
- Next ADR will be `####` (4-digit zero-padded)

**Identify participants (optional):**

Ask: "Who should participate in reviewing this decision? (optional)"

Provide guidance:
```
You can provide names (first names, nicknames, or full names).
I'll match them against git authors to populate the participants list.

Leave blank to skip - participants will be added as people engage.

Examples: "alice, bob" or "Alice Chen, Bob Smith"
```

If names provided:
1. Get all git authors: `git log --all --format='%an' | sort -u`
2. Fuzzy match each provided name:
   - Case-insensitive matching
   - Match on first name, last name, or full name
   - Extract username as lowercase first word from matched git author
   - Example: "Alice Chen" → username "alice"
   - Show matches for confirmation
3. Confirm matches with user:
   ```
   I found these git authors:
   - alice (Alice Chen)
   - bob (Bob Smith)

   Add them as participants? [Y/N]
   ```
4. If confirmed, set in frontmatter:
   ```yaml
   discussion:
     participants: [alice, bob]
     unread_by: [alice, bob]
     started: {current_date}
     last_updated: {current_date}
   ```

If no names provided or skipped:
```yaml
discussion:
  participants: []
  unread_by: []
  started: {current_date}
  last_updated: {current_date}
```

**Read existing ADRs for context:**
- Use Glob to find ADRs in `PROJECT_ROOT/.tasty-dev/adr/`
- If ADRs exist: read them to understand existing decisions, build context for suggestions and conflict detection
- If no ADRs exist: note this is the first ADR; use generic software engineering examples throughout the workflow (e.g., database selection, API versioning, monorepo vs polyrepo)
```

---

### Task 8: Rewrite Skill — Steps 2-4 (Clarify, Drivers, Explore Options)

**Files:**
- Modify: `skills/adr/skill.md`

**Step 1: Replace Step 2 (Clarify the Decision)**

Replace the entire "### Step 2" section (original lines 133-150) with:

```markdown
### Step 2: Clarify the Decision

Ask two foundational questions:

**Q1: What decision are we making?**
- Example (generic): "Should we use PostgreSQL or DynamoDB for our persistence layer?"
- Example (context-aware, if ADRs exist): Reference a related existing ADR to frame the question

**Q2: What problem does this solve?**
- Example (generic): "We need to choose a database but have conflicting requirements between query flexibility and write throughput."
- Example (context-aware): Reference related patterns from existing ADRs

Capture clear, specific answers before proceeding.
```

**Step 2: Replace Step 3 (Decision Drivers)**

Replace the entire "### Step 3" section (original lines 152-167). The content is already domain-agnostic — keep it as-is but confirm no hardcoded references exist. The current content is clean.

**Step 3: Replace Step 4 (Explore Options)**

Replace the entire "### Step 4" section (original lines 169-282) with:

```markdown
### Step 4: Explore Options

This is a critical step with 5 substeps:

#### 4a. Present Known Options

Ask the user to describe the options they're considering.

If existing ADRs are relevant, reference them:
```
Based on your existing ADRs, I see related decisions:

Option 1: {pattern from existing ADR}
- Established by: ADR-{NNNN} ({title})

Are there other options you want to consider?
```

If no existing ADRs exist, simply ask:
```
What options are you considering? Describe at least two approaches.
```

#### 4b. Offer to Suggest Additional Options

```
Would you like me to suggest additional options based on:
- Related ADRs in this project
- Common patterns for this type of decision
- Trade-offs you may not have considered

[Yes, suggest alternatives] [No, continue with current options]
```

#### 4c. Generate Suggestions (If requested)

Analyze existing ADRs and the project context to generate suggestions:

**Analysis process:**
1. Read related ADRs to identify patterns and precedents
2. Consider common industry approaches for this type of decision
3. Generate 1-3 additional options with rationale

**Example suggestion (context-aware):**
```
Based on ADR-{NNNN} ({title}) and the patterns in this project:

Option 3: {suggested approach}
Source: Extends the pattern established in ADR-{NNNN}
Pros:
- {pro 1}
- {pro 2}
Cons:
- {con 1}
- {con 2}

Rationale: {why this option is relevant given existing decisions}

Does this option make sense for your context? Should we include it?
```

**Example suggestion (generic, no existing ADRs):**
```
Based on common approaches for this type of decision:

Option 3: {suggested approach}
Pros:
- {pro 1}
- {pro 2}
Cons:
- {con 1}

This is a common choice when {context}. Does this option make sense?
```

#### 4d. Validate Suggestions

For each suggestion:
- Explain the rationale and source
- Ask if it's relevant to their context
- Only include options the human validates

#### 4e. Collaborate on Pros/Cons

For each option (both known and suggested):
```
Let's detail Option 1: {name}

Current pros:
- {pro 1}
- {pro 2}

Current cons:
- {con 1}

What would you add or change?
```

#### 4f. Get Recommendation

After analyzing all options:
```
Based on the decision drivers you selected:
- {driver 1} (high priority)
- {driver 2} (medium priority)

I recommend: Option {N} ({name})

Reasoning:
- {reason tied to driver 1}
- {reason tied to driver 2}
- {reason tied to existing ADR precedent, if applicable}

However, Option {M} ({name}) would be preferable if:
- {condition 1}
- {condition 2}

What's your preference?
```
```

---

### Task 9: Rewrite Skill — Steps 5-7 (Skeptical Review, Metadata, Consequences)

**Files:**
- Modify: `skills/adr/skill.md`

**Step 1: Replace Step 5 (Skeptical Review)**

Replace the entire "### Step 5" section (original lines 284-349) with:

```markdown
### Step 5: Skeptical Review

This is a critical step with 2 substeps:

#### 5a. Challenge the Decision

Play devil's advocate with 4 specific challenge types:

```
Let me challenge this decision to help you defend it.

Your preference: Option {N} ({name})

**1. Consistency Issue**
   - Does this conflict with any existing ADRs?
   - If existing ADRs reference related patterns, call out specific conflicts
   - If this is the first ADR, consider: does this set a precedent you're comfortable with?

**2. Historical Precedent**
   - Has a similar decision been made before in this project?
   - Check existing ADRs for related decisions and whether this aligns or diverges
   - If no precedent exists, note that this establishes new ground

**3. Foundational Principle Challenge**
   - Does this align with the project's stated principles and decision drivers?
   - Are you trading off a principle you previously prioritized?
   - If so, should you revisit that earlier decision?

**4. Migration Cost**
   - What existing code, configuration, or processes need changing?
   - What are the downstream dependencies?
   - Is the benefit worth the migration effort?
   - Have you estimated the scope of change?

How would you respond to these concerns?
```

**Challenge generation guidelines:**
1. **Consistency Issue**: Identify conflicts with existing ADRs in `PROJECT_ROOT/.tasty-dev/adr/`
2. **Historical Precedent**: Check if past decisions apply differently
3. **Foundational Principle Challenge**: Check against stated decision drivers and earlier ADRs
4. **Migration Cost**: Quantify change impact and question ROI

Let human respond to each challenge. This forces them to defend their decision or reconsider.

#### 5b. Status Decision

After skeptical review:
```
Based on your responses to the challenges, what's the status?

1. **Finalize as proposed**: Write the ADR with your chosen option
2. **Save as draft**: Write ADR with status: draft for later review
3. **Revise options**: Go back to Step 4 to reconsider options

Your choice:
```
```

**Step 2: Replace Step 6 (Define Metadata)**

Replace the entire "### Step 6" section (original lines 351-443) with:

```markdown
### Step 6: Define Metadata

#### 6a. Domains

Suggest domains based on content:
```
This decision affects which architectural domains?

Suggest domains based on the decision content and existing ADRs.
If existing ADRs use domain tags, suggest consistent terminology.

Select applicable or add others:
```

#### 6b. Affects

Identify impacted areas:
```
What areas are affected by this decision?

Suggest affected areas based on the decision content and codebase.

Select applicable or add others:
```

#### 6c. Enforces (Placeholder)

Note: Enforcement rules are not yet active. The `enforces` field in the ADR frontmatter will be populated in a future phase when the tasty-dev enforcement system is built (Phase 2.5). For now, leave the field as an empty list.

#### 6d. Relationships

Identify relationships to other ADRs:
```
Relationships to other ADRs:

Suggested (based on reading existing ADRs in PROJECT_ROOT/.tasty-dev/adr/):
- supersedes: (list any ADRs this replaces)
- related_to: (list any ADRs that address similar concerns)

Modify or add relationships:
```
```

**Step 3: Step 7 (Consequences) is already domain-agnostic**

Review the existing Step 7 section (original lines 445-473). It contains no hardcoded paths or domain references. Keep it as-is.

---

### Task 10: Rewrite Skill — Steps 8-9 (Write ADR, Maintenance)

**Files:**
- Modify: `skills/adr/skill.md`

**Step 1: Replace Step 8 (Write ADR File)**

Replace the entire "### Step 8" section (original lines 475-586) with:

```markdown
### Step 8: Write ADR File

Generate complete MADR file using the template at `templates/adr-template.md`:

```
I'll create the ADR:

Filename: PROJECT_ROOT/.tasty-dev/adr/####-{slug}.md
Status: {proposed|draft}
```

**MADR format** — use the template from `templates/adr-template.md`, filling in:
- Frontmatter: status, date, decision-makers, consulted, informed, domains, affects, related, supersedes, discussion metadata
- Body: Context from Step 2, drivers from Step 3, options from Step 4, outcome from Steps 4f/5, consequences from Step 7, pros/cons from Step 4e

**Show preview:**
```
Here's the ADR content:

[Show first 30 lines]

...

[Show last 10 lines]

Ready to write to PROJECT_ROOT/.tasty-dev/adr/####-{slug}.md?
[Write file] [Make changes] [Cancel]
```

**Write file** (if approved):
- Use Write tool to create file
- Confirm file written successfully
```

**Step 2: Replace Step 9 (Maintenance Tasks)**

Replace the entire "### Step 9" section (original lines 588-620) with:

```markdown
### Step 9: Maintenance Tasks

After writing ADR:

#### 9a. Update Related ADRs

If the new ADR has relationships to existing ADRs:

```
Should I update related ADRs?

ADR-{NNNN} ({title}):
- Add to "related" frontmatter: ADR-{new number}
- {Any content notes if applicable}

Make these updates?
[Yes] [No] [Let me review first]
```

If approved, use Edit tool to update related ADRs in `PROJECT_ROOT/.tasty-dev/adr/`.

#### 9b. Summary

```
ADR-{NNNN} created: PROJECT_ROOT/.tasty-dev/adr/####-{slug}.md

Files modified:
- Created: .tasty-dev/adr/####-{slug}.md
- Updated: .tasty-dev/adr/{related ADRs if any}

Files are ready for you to commit when ready.
```
```

---

### Task 11: Rewrite Skill — Review Mode

**Files:**
- Modify: `skills/adr/skill.md`

**Step 1: Replace Review Mode section**

Replace the entire "## Review Mode" section (original lines 628-677) with:

```markdown
## Review Mode

Review mode has two invocation patterns:

### Pattern 1: Review Specific ADR

```bash
/adr-author --review .tasty-dev/adr/0004-some-decision.md
```

**Behavior:** Jump directly to reviewing that specific ADR (see Single ADR Review Workflow below).

### Pattern 2: Review All Unread ADRs

```bash
/adr-author --review
```

**Behavior:** Find and review all ADRs needing attention sequentially.

**Detection logic:**

1. **Get current user identity:**
   ```bash
   git config user.name | awk '{print tolower($1)}'
   ```

2. **Find all ADR files:**
   Use Glob to find `PROJECT_ROOT/.tasty-dev/adr/*.md` matching pattern `[0-9][0-9][0-9][0-9]-*`

3. **For each ADR, check if review needed:**
   - Read frontmatter
   - Check: `status != "draft"` (only review proposed/accepted ADRs)
   - Check: `current_user NOT IN discussion.participants` OR `current_user IN discussion.unread_by`
   - If both conditions true, add to review queue

4. **Present queue:**
   ```
   Found 3 ADRs needing your review:
   1. ADR-0004: Bridge Foreign Key Pattern (2 new comments)
   2. ADR-0005: Deferred Promotion Pattern (not yet reviewed)
   3. ADR-0006: Auditability Pattern (4 new comments)

   Starting with ADR-0004...
   ```

5. **Process each ADR sequentially** using Single ADR Review Workflow

**Edge cases:**
- No ADRs need review: "All ADRs are up to date! You've reviewed everything."
- Only draft ADRs exist: "No proposed or accepted ADRs need review yet."
- Git config fails: Ask user for their name
```

**Step 2: Replace Single ADR Review Workflow**

Replace the "### Single ADR Review Workflow" section (original lines 683-735) — this section is already project-agnostic. Keep the content as-is, no changes needed. Verify no hardcoded paths exist.

---

### Task 12: Rewrite Skill — Chronological Navigation

**Files:**
- Modify: `skills/adr/skill.md`

**Step 1: Replace Chronological Navigation section**

Replace the "## Chronological Navigation (Commit History)" section (original lines 737-831). Update the git commands to use `PROJECT_ROOT` instead of hardcoded paths:

In Step 1, replace:
```bash
cd /Users/zac.propersi/projects/gitlab/core_data_pipeline
git log --reverse --format='%H|%an|%ad|%s' --date=format:'%Y-%m-%d %H:%M' -- docs/adr/XXXX-*.md
```

With:
```bash
git log --reverse --format='%H|%an|%ad|%s' --date=format:'%Y-%m-%d %H:%M' -- PROJECT_ROOT/.tasty-dev/adr/XXXX-*.md
```

The rest of the Chronological Navigation section is project-agnostic. Keep Steps 2-6 as-is.

---

### Task 13: Rewrite Skill — Discussion, Comments, Approval, AI Facilitator, Git Workflow

**Files:**
- Modify: `skills/adr/skill.md`

**Step 1: Update Discussion Section Management**

In the "## Discussion Section Management" section, the "### Adding Comments to ADR Files" subsection (original lines 888-920) references the hardcoded path. Replace all occurrences of:
```
/Users/zac.propersi/projects/gitlab/core_data_pipeline/docs/adr/XXXX-*.md
```
With:
```
PROJECT_ROOT/.tasty-dev/adr/XXXX-*.md
```

There are 3 occurrences in this section:
- Line 892 (Step 1: Read current ADR file)
- Line 920 (Step 7: Verify modification)
- Also check the Comment Review Workflow and Approval Workflow sections for any remaining hardcoded paths

**Step 2: Update Comment Review Workflow**

The "## Comment Review Workflow" section (original lines 922-1020) is project-agnostic. No path changes needed. Keep as-is.

**Step 3: Update Approval Workflow**

The "## Approval Workflow" section (original lines 1022-1120) is project-agnostic. No path changes needed. Keep as-is.

**Step 4: Update Claude as AI Facilitator**

The "## Claude as AI Facilitator" section (original lines 1122-1220) is project-agnostic. No path changes needed. Keep as-is.

**Step 5: Update Git Commit Workflow**

The "## Git Commit Workflow" section (original lines 1222-1276) references `docs/adr/` in git commands. Replace with `.tasty-dev/adr/`:

Replace:
```bash
git status docs/adr/
git diff docs/adr/*.md | head -50
```
With:
```bash
git status .tasty-dev/adr/
git diff .tasty-dev/adr/*.md
```

**Step 6: Update Notes section**

Replace the "## Notes" section (original lines 1278-1295) with:

```markdown
## Notes

- **Dynamic path resolution**: Always resolve `PROJECT_ROOT` via `.tasty-dev/config.yaml` discovery at session start (see Project Root Resolution)
- **Context-aware examples**: When existing ADRs are present, derive examples and suggestions from them. When none exist, use generic software engineering examples.
- **Skeptical review is mandatory**: Don't skip Step 5a challenges
- **Suggestion engine is optional**: Only run Step 4c if human requests it
- **Be conversational**: This is a guided conversation, not a form to fill out
- **One step at a time**: Don't rush through steps; ensure clarity before proceeding
- **Save progress**: If conversation is interrupted, human can resume with `--review`
- **Enforces field**: Leave as empty list until Phase 2.5 enforcement system is built
```

---

### Task 14: Rewrite Skill — User Identity and Example Invocations

**Files:**
- Modify: `skills/adr/skill.md`

**Step 1: Update User Identity Detection section**

The "## User Identity Detection" section (original lines 1297-1333) is already project-agnostic. No changes needed. Keep as-is.

**Step 2: Replace Example Invocations section**

Replace the entire "## Example Invocations" section (original lines 1335-1593) with:

```markdown
## Example Invocations

### Creating new ADR from scratch

```
User: /adr-author
Claude: I'll help you create a new ADR. Let me start by finding your project's ADR directory...

[Resolves PROJECT_ROOT via .tasty-dev/config.yaml]
[Reads existing ADRs, determines next number is 0003]

We'll create ADR-0003.

Who should participate in reviewing this decision? (optional)

You can provide names (first names, nicknames, or full names).
I'll match them against git authors to populate the participants list.

Leave blank to skip - participants will be added as people engage.

User: alice, bob

Claude: [Runs git log --all --format='%an' | sort -u]

I found these git authors:
- alice (Alice Johnson)
- bob (Bob Martinez)

Add them as participants? [Y/N]

User: Y

Claude: Great. Now, what decision are we making?

[... rest of 9-step workflow continues ...]
```

### Reviewing unread ADRs

```
User: /adr-author --review

Claude: Let me find ADRs needing your review...

[Detects user identity: "zac" from git config]
[Scans PROJECT_ROOT/.tasty-dev/adr/ for unread ADRs]

Found 2 ADRs needing your review:
1. ADR-0001: Use PostgreSQL for Persistence (3 comments, last by Bob)
2. ADR-0002: API Versioning Strategy (not yet reviewed)

Starting with ADR-0001...

=== ADR-0001: Use PostgreSQL for Persistence ===
Status: proposed

Summary: Proposes PostgreSQL with connection pooling for the
application persistence layer.

Discussion status: 3 comments, last by Bob on 2026-03-20.
You haven't responded yet.

How would you like to review?
[C] Chronological | [L] Latest | [F] Full

[... review workflow continues ...]
```

### Reviewing a specific ADR

```
User: /adr-author --review .tasty-dev/adr/0001-use-postgresql-for-persistence.md

Claude: [Reads ADR, parses frontmatter and discussion]

=== ADR-0001: Use PostgreSQL for Persistence ===
Status: proposed

Summary: Proposes PostgreSQL with connection pooling for the
application persistence layer.

How would you like to review?
[C] Chronological | [L] Latest | [F] Full

[... review workflow continues ...]
```
```

---

### Task 15: Rewrite TESTING.md

**Files:**
- Modify: `skills/adr/TESTING.md`

**Step 1: Replace the entire contents of TESTING.md**

```markdown
# ADR Author Skill — Development Testing

Development-time validation for the adapted ADR author skill.
These materials are used during skill development and stay in this repo.
They do not ship with the plugin.

## Seed Test Project Setup

Create a temporary test project to exercise review/discussion features:

```bash
# Create test project
mkdir -p /tmp/adr-test-project
cd /tmp/adr-test-project
git init
bin/init-project-storage .
```

### Seed ADR 1: Proposed with Discussion

Write to `.tasty-dev/adr/0001-use-postgresql-for-persistence.md`:

```markdown
---
status: proposed
date: 2026-03-20
decision-makers: [zac, alice]
consulted: []
informed: []
domains: [infrastructure, data]
affects: [backend, deployment]
related: []
supersedes: []
enforces: []
discussion:
  participants: [zac, alice, bob]
  unread_by: [zac]
  started: 2026-03-20
  last_updated: 2026-03-25
---

# Use PostgreSQL for Persistence

## Context and Problem Statement

We need a database for our application. The team has experience with both PostgreSQL and MongoDB, but we need ACID compliance for financial transactions.

## Decision Drivers

* ACID compliance for financial data
* Team familiarity
* Operational simplicity

## Considered Options

* Option 1: PostgreSQL with connection pooling
* Option 2: MongoDB with transactions
* Option 3: CockroachDB for distributed SQL

## Decision Outcome

Chosen option: "Option 1: PostgreSQL with connection pooling", because it provides native ACID compliance with the lowest operational overhead and highest team familiarity.

### Consequences

* Good, because team already knows PostgreSQL well
* Good, because ACID compliance is native, not bolted on
* Bad, because horizontal scaling requires more effort than MongoDB
* Neutral, because connection pooling adds a component to manage

## Pros and Cons of the Options

### Option 1: PostgreSQL with connection pooling

Mature RDBMS with strong ACID support.

* Good, because native ACID compliance
* Good, because team has 5+ years experience
* Good, because excellent tooling ecosystem
* Bad, because horizontal scaling is complex
* Bad, because connection pooling adds operational overhead

### Option 2: MongoDB with transactions

Document database with multi-document transaction support since 4.0.

* Good, because flexible schema for evolving data models
* Good, because built-in horizontal scaling
* Bad, because transaction support is newer and less battle-tested
* Bad, because team has limited MongoDB experience

### Option 3: CockroachDB for distributed SQL

Distributed SQL database with PostgreSQL wire compatibility.

* Good, because horizontal scaling with SQL interface
* Good, because PostgreSQL compatible (familiar syntax)
* Bad, because higher operational complexity
* Bad, because smaller ecosystem and community

## Discussion

### Comment by Alice (2026-03-22 10:30)

I'm concerned about the connection pooling overhead. Have we looked at PgBouncer vs pgpool-II?

#### Reply by Bob (2026-03-25 14:00)

Good point Alice. I've used PgBouncer in production — it's much lighter weight than pgpool-II. I'd recommend PgBouncer in transaction mode.

## More Information
```

### Seed ADR 2: Draft with No Discussion

Write to `.tasty-dev/adr/0002-api-versioning-strategy.md`:

```markdown
---
status: draft
date: 2026-03-25
decision-makers: [zac]
consulted: []
informed: []
domains: [api-design]
affects: [backend, frontend, documentation]
related: []
supersedes: []
enforces: []
discussion:
  participants: [zac]
  unread_by: []
  started: 2026-03-25
  last_updated: 2026-03-25
---

# API Versioning Strategy

## Context and Problem Statement

As we prepare for external API consumers, we need a versioning strategy that allows evolution without breaking existing integrations.

## Decision Drivers

* Backward compatibility for consumers
* Developer experience
* Ease of deprecation

## Considered Options

* Option 1: URL path versioning (/v1/, /v2/)
* Option 2: Header-based versioning (Accept-Version)

## Decision Outcome

Pending — draft for team discussion.

### Consequences

TBD

## Pros and Cons of the Options

### Option 1: URL path versioning

* Good, because immediately visible in URLs
* Good, because simple to implement and route
* Bad, because proliferates URL paths

### Option 2: Header-based versioning

* Good, because cleaner URLs
* Bad, because less discoverable
* Bad, because harder to test in browser

## Discussion

## More Information
```

## Test Scenarios

### Scenario 1: Creation Workflow

**Invoke:** `/adr-author`

**Validate:**
- Project root resolved correctly via `.tasty-dev/config.yaml`
- Next ADR number detected as 0003 (based on seed data)
- Context-aware examples reference existing ADRs (PostgreSQL, API versioning)
- All 9 steps execute in order
- Skeptical review references existing ADR decisions
- Output file is valid MADR with correct frontmatter
- File written to `.tasty-dev/adr/0003-{slug}.md`

### Scenario 2: Review All Unread

**Invoke:** `/adr-author --review`

**Validate:**
- User identity detected from git config
- ADR-0001 shows as needing review (zac in unread_by)
- ADR-0002 is skipped (status: draft)
- Review queue presented correctly
- Comment/reply threading works
- Frontmatter updated after interaction

### Scenario 3: Review Specific ADR

**Invoke:** `/adr-author --review .tasty-dev/adr/0001-use-postgresql-for-persistence.md`

**Validate:**
- ADR loaded and summarized
- All viewing modes work (Chronological, Latest, Full)
- Comment workflow includes critical analysis
- Approval workflow changes status

### Scenario 4: Bootstrap on Fresh Project

**Invoke:** `/adr-author` in a project without `.tasty-dev/`

**Validate:**
- Skill detects missing `.tasty-dev/`
- Offers to run `init-project-storage`
- After init, proceeds with creation workflow
- Generic examples used (no existing ADRs)

## Success Criteria

- Project root resolved via .tasty-dev/config.yaml discovery
- Context-aware examples derived from existing ADRs when present
- Generic examples used when no ADRs exist
- All 9 creation steps complete without hardcoded references
- Review queue correctly identifies unread ADRs
- Comment threading and critical analysis functional
- Approval workflow updates frontmatter status
- No references to core_data_pipeline, Databricks, Unity Catalog, or guardian skills
- Manual commit mode (no auto-commits)
```

---

### Task 16: Final Verification

**Files:**
- Read: all modified files for consistency check

**Step 1: Run all tests**

Run: `cd /Users/zac.propersi/projects/github/claude-skillz/tasty-dev && python3 -m pytest tests/ -v`
Expected: All tests pass

**Step 2: Verify no hardcoded paths remain in skill**

Run: `cd /Users/zac.propersi/projects/github/claude-skillz/tasty-dev && grep -r "core_data_pipeline\|gitlab/core\|databricks\|unity.catalog\|DLT\|medallion\|guardian" skills/adr/`
Expected: No matches

**Step 3: Verify no references to removed CLI tools**

Run: `cd /Users/zac.propersi/projects/github/claude-skillz/tasty-dev && grep -r "bin/create-adr\|bin/query-adr" . --include="*.md" --include="*.py" | grep -v ".git/"`
Expected: No matches

**Step 4: Verify MADR template referenced consistently**

Run: `cd /Users/zac.propersi/projects/github/claude-skillz/tasty-dev && grep -r "adr-template" skills/ templates/`
Expected: Template referenced in skill, exists in templates/

**Step 5: Read through skill.md end-to-end**

Use Read tool on `skills/adr/skill.md` to do a final human review for:
- Coherent flow from section to section
- No orphaned references to removed features
- PROJECT_ROOT used consistently (never hardcoded)
- Context-aware example pattern used in Steps 1, 2, 4, 5

**Step 6: Commit all remaining changes**

```
feat(adr): adapt adr-author skill for tasty-dev architecture
```
