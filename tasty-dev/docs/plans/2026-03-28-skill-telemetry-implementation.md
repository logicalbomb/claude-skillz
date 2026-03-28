# Skill Telemetry — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add invocation trace telemetry to all tasty-dev skills and build a health assessment skill for analyzing collected traces.

**Architecture:** Each skill checks `~/.tasty-dev/config.toml` for telemetry toggle, then writes a step-level markdown trace to `~/.tasty-dev/telemetry/{git-remote-slug}/`. Each skill declares expected usage in its frontmatter. A health assessment skill (development-time only) reads traces and evaluates against expectations.

**Tech Stack:** Python (user-level init, TOML parsing), Markdown (skill files, trace files), TOML (config)

**Design doc:** `docs/plans/2026-03-28-skill-telemetry-design.md`

---

### Task 1: Create User-Level Init Script

**Files:**
- Create: `bin/init-user-config`
- Test: `tests/test_user_config.py`

**Step 1: Write the failing test**

```python
# tests/test_user_config.py
"""Tests for user-level config initialization."""
import subprocess
import tempfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def test_init_user_config_creates_config_toml(tmp_path, monkeypatch):
    """init-user-config creates config.toml with telemetry disabled."""
    config_dir = tmp_path / ".tasty-dev"
    result = subprocess.run(
        ["bin/init-user-config"],
        capture_output=True,
        text=True,
        env={"TASTYDEV_USER_DIR": str(config_dir), "PATH": ""},
    )

    assert result.returncode == 0
    config_path = config_dir / "config.toml"
    assert config_path.exists()

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    assert config["telemetry"]["enabled"] is False


def test_init_user_config_creates_telemetry_dir(tmp_path):
    """init-user-config creates the telemetry directory."""
    config_dir = tmp_path / ".tasty-dev"
    subprocess.run(
        ["bin/init-user-config"],
        capture_output=True,
        env={"TASTYDEV_USER_DIR": str(config_dir), "PATH": ""},
    )

    assert (config_dir / "telemetry").is_dir()


def test_init_user_config_is_idempotent(tmp_path):
    """Running init-user-config twice does not overwrite config."""
    config_dir = tmp_path / ".tasty-dev"

    # First run
    subprocess.run(
        ["bin/init-user-config"],
        capture_output=True,
        env={"TASTYDEV_USER_DIR": str(config_dir), "PATH": ""},
    )

    # Modify config
    config_path = config_dir / "config.toml"
    config_path.write_text('[telemetry]\nenabled = true\n')

    # Second run
    subprocess.run(
        ["bin/init-user-config"],
        capture_output=True,
        env={"TASTYDEV_USER_DIR": str(config_dir), "PATH": ""},
    )

    # Should retain modification
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    assert config["telemetry"]["enabled"] is True
```

**Step 2: Run test to verify it fails**

Run: `source venv/bin/activate && python -m pytest tests/test_user_config.py -v`
Expected: FAIL — `bin/init-user-config` does not exist

**Step 3: Write the init script**

```python
#!/usr/bin/env python3
# bin/init-user-config
"""Initialize user-level ~/.tasty-dev config and telemetry directory."""
import os
import sys
from pathlib import Path


def get_user_dir() -> Path:
    """Get user-level tasty-dev directory, respecting env override for testing."""
    override = os.environ.get("TASTYDEV_USER_DIR")
    if override:
        return Path(override)
    return Path.home() / ".tasty-dev"


def init_user_config() -> None:
    """Create user-level config and telemetry directory."""
    user_dir = get_user_dir()
    user_dir.mkdir(parents=True, exist_ok=True)

    # Create telemetry directory
    telemetry_dir = user_dir / "telemetry"
    telemetry_dir.mkdir(exist_ok=True)

    # Create config only if it doesn't exist
    config_path = user_dir / "config.toml"
    if not config_path.exists():
        config_path.write_text('[telemetry]\nenabled = false\n')
        print(f"Created {config_path}")
    else:
        print(f"Config already exists: {config_path}")


if __name__ == "__main__":
    init_user_config()
```

Make it executable: `chmod +x bin/init-user-config`

**Step 4: Install tomli for Python < 3.11 compatibility**

Run: `source venv/bin/activate && pip install tomli`

Add `tomli>=2.0.0;python_version<"3.11"` to `requirements.txt`.

**Step 5: Run test to verify it passes**

Run: `source venv/bin/activate && python -m pytest tests/test_user_config.py -v`
Expected: All 3 tests PASS

**Step 6: Commit**

```
feat(telemetry): add user-level init script for config.toml and telemetry dir
```

---

### Task 2: Create Telemetry Writer Utility

A shared Python utility that skills can reference for writing traces. This avoids duplicating trace-writing logic across every skill's instructions.

**Files:**
- Create: `bin/write-telemetry-trace`
- Test: `tests/test_telemetry_writer.py`

**Step 1: Write the failing tests**

```python
# tests/test_telemetry_writer.py
"""Tests for telemetry trace writer."""
import json
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def _setup_user_dir(tmp_path: Path) -> Path:
    """Create a user dir with telemetry enabled."""
    user_dir = tmp_path / ".tasty-dev"
    user_dir.mkdir()
    (user_dir / "telemetry").mkdir()
    (user_dir / "config.toml").write_text('[telemetry]\nenabled = true\n')
    return user_dir


def test_write_trace_creates_file(tmp_path):
    """write-telemetry-trace creates a trace file in the correct location."""
    user_dir = _setup_user_dir(tmp_path)

    trace_data = json.dumps({
        "skill": "adr-author",
        "skill_version": "0.1.0",
        "tastydev_version": "0.1.0",
        "mode": "review",
        "project": "git@github.com:org/project-alpha.git",
        "user": "zac",
        "steps": [
            {"status": "completed", "description": "Resolve project root", "detail": "found .tasty-dev/config.yaml"}
        ],
        "outcome": ["ADRs reviewed: 1"],
        "issues": []
    })

    result = subprocess.run(
        ["bin/write-telemetry-trace"],
        input=trace_data,
        capture_output=True,
        text=True,
        env={"TASTYDEV_USER_DIR": str(user_dir), "PATH": ""},
    )

    assert result.returncode == 0

    # Check file was created in correct project directory
    project_dir = user_dir / "telemetry" / "github.com-org-project-alpha"
    assert project_dir.is_dir()

    trace_files = list(project_dir.glob("*-adr-author.md"))
    assert len(trace_files) == 1


def test_write_trace_has_correct_structure(tmp_path):
    """Trace file has YAML frontmatter and markdown body."""
    user_dir = _setup_user_dir(tmp_path)

    trace_data = json.dumps({
        "skill": "adr-author",
        "skill_version": "0.1.0",
        "tastydev_version": "0.1.0",
        "mode": "create",
        "project": "git@github.com:org/project-alpha.git",
        "user": "zac",
        "steps": [
            {"status": "completed", "description": "Step 1", "detail": "done"}
        ],
        "outcome": ["ADRs created: 1"],
        "issues": ["User skipped skeptical review"]
    })

    subprocess.run(
        ["bin/write-telemetry-trace"],
        input=trace_data,
        capture_output=True,
        text=True,
        env={"TASTYDEV_USER_DIR": str(user_dir), "PATH": ""},
    )

    project_dir = user_dir / "telemetry" / "github.com-org-project-alpha"
    trace_file = list(project_dir.glob("*.md"))[0]
    content = trace_file.read_text()

    assert content.startswith("---")
    assert "skill: adr-author" in content
    assert "## Steps" in content
    assert "## Outcome" in content
    assert "## Issues" in content
    assert "User skipped skeptical review" in content


def test_write_trace_skips_when_disabled(tmp_path):
    """write-telemetry-trace does nothing when telemetry is disabled."""
    user_dir = tmp_path / ".tasty-dev"
    user_dir.mkdir()
    (user_dir / "telemetry").mkdir()
    (user_dir / "config.toml").write_text('[telemetry]\nenabled = false\n')

    trace_data = json.dumps({
        "skill": "adr-author",
        "skill_version": "0.1.0",
        "tastydev_version": "0.1.0",
        "mode": "review",
        "project": "git@github.com:org/test.git",
        "user": "zac",
        "steps": [],
        "outcome": [],
        "issues": []
    })

    result = subprocess.run(
        ["bin/write-telemetry-trace"],
        input=trace_data,
        capture_output=True,
        text=True,
        env={"TASTYDEV_USER_DIR": str(user_dir), "PATH": ""},
    )

    assert result.returncode == 0
    # No project directory created
    telemetry_dir = user_dir / "telemetry"
    assert list(telemetry_dir.iterdir()) == []


def test_write_trace_skips_when_no_config(tmp_path):
    """write-telemetry-trace does nothing when config.toml is missing."""
    user_dir = tmp_path / ".tasty-dev"
    user_dir.mkdir()
    (user_dir / "telemetry").mkdir()
    # No config.toml created

    trace_data = json.dumps({
        "skill": "adr-author",
        "skill_version": "0.1.0",
        "tastydev_version": "0.1.0",
        "mode": "review",
        "project": "git@github.com:org/test.git",
        "user": "zac",
        "steps": [],
        "outcome": [],
        "issues": []
    })

    result = subprocess.run(
        ["bin/write-telemetry-trace"],
        input=trace_data,
        capture_output=True,
        text=True,
        env={"TASTYDEV_USER_DIR": str(user_dir), "PATH": ""},
    )

    assert result.returncode == 0
    telemetry_dir = user_dir / "telemetry"
    assert list(telemetry_dir.iterdir()) == []
```

**Step 2: Run tests to verify they fail**

Run: `source venv/bin/activate && python -m pytest tests/test_telemetry_writer.py -v`
Expected: FAIL — `bin/write-telemetry-trace` does not exist

**Step 3: Write the trace writer script**

```python
#!/usr/bin/env python3
# bin/write-telemetry-trace
"""Write a telemetry invocation trace. Reads JSON from stdin."""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def get_user_dir() -> Path:
    """Get user-level tasty-dev directory, respecting env override for testing."""
    override = os.environ.get("TASTYDEV_USER_DIR")
    if override:
        return Path(override)
    return Path.home() / ".tasty-dev"


def is_telemetry_enabled(user_dir: Path) -> bool:
    """Check if telemetry is enabled in user config."""
    config_path = user_dir / "config.toml"
    if not config_path.exists():
        return False
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    return config.get("telemetry", {}).get("enabled", False)


def slugify_remote(remote: str) -> str:
    """Convert git remote URL to filesystem-safe slug."""
    slug = remote.replace("git@", "").replace("https://", "")
    slug = re.sub(r"[:/]", "-", slug)
    slug = slug.rstrip(".git").rstrip("-")
    return slug


def format_trace(data: dict, timestamp: str) -> str:
    """Format trace data as markdown with YAML frontmatter."""
    lines = [
        "---",
        f"skill: {data['skill']}",
        f"skill_version: {data['skill_version']}",
        f"tastydev_version: {data['tastydev_version']}",
        f"mode: {data['mode']}",
        f"project: {data['project']}",
        f"user: {data['user']}",
        f"timestamp: {timestamp}",
        "---",
        "",
        "## Steps",
        "",
    ]

    for step in data.get("steps", []):
        detail = f" — {step['detail']}" if step.get("detail") else ""
        lines.append(f"- [{step['status']}] {step['description']}{detail}")

    lines.extend(["", "## Outcome", ""])
    for item in data.get("outcome", []):
        lines.append(f"- {item}")
    if not data.get("outcome"):
        lines.append("None")

    lines.extend(["", "## Issues", ""])
    for item in data.get("issues", []):
        lines.append(f"- {item}")
    if not data.get("issues"):
        lines.append("None")

    lines.append("")
    return "\n".join(lines)


def write_trace() -> None:
    """Read JSON from stdin and write trace file."""
    user_dir = get_user_dir()

    if not is_telemetry_enabled(user_dir):
        return

    data = json.load(sys.stdin)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M")

    # Create project directory
    project_slug = slugify_remote(data["project"])
    project_dir = user_dir / "telemetry" / project_slug
    project_dir.mkdir(parents=True, exist_ok=True)

    # Write trace file
    filename = f"{timestamp}-{data['skill']}.md"
    trace_path = project_dir / filename
    trace_path.write_text(format_trace(data, timestamp))

    print(f"Trace written: {trace_path}")


if __name__ == "__main__":
    write_trace()
```

Make it executable: `chmod +x bin/write-telemetry-trace`

**Step 4: Run tests to verify they pass**

Run: `source venv/bin/activate && python -m pytest tests/test_telemetry_writer.py -v`
Expected: All 5 tests PASS

**Step 5: Commit**

```
feat(telemetry): add trace writer utility
```

---

### Task 3: Add Version and Telemetry Expectations to All Skills

**Files:**
- Modify: `skills/adr/skill.md:1-4`
- Modify: `skills/reflexion/capture.md:1-4`
- Modify: `skills/reviews/project-weekly.md:1-4`
- Modify: `skills/superpowers-enhanced/brainstorming-enhanced.md:1-4`
- Modify: `skills/superpowers-enhanced/writing-plans-enhanced.md:1-4`

**Step 1: Update adr-author frontmatter**

In `skills/adr/skill.md`, replace:

```yaml
---
name: adr-author
description: Guide creation and review of architecture decision records through conversational workflow
---
```

With:

```yaml
---
name: adr-author
description: Guide creation and review of architecture decision records through conversational workflow
version: 0.1.0
telemetry:
  expected_cadence: on_demand
  expected_participants: all
  health_signals:
    - "at least 1 invocation per project per month"
    - "review mode should run within 7 days of a new proposed ADR"
---
```

**Step 2: Update reflexion-capture frontmatter**

In `skills/reflexion/capture.md`, replace:

```yaml
---
name: reflexion-capture
description: Capture a development insight or decision through reflexion
---
```

With:

```yaml
---
name: reflexion-capture
description: Capture a development insight or decision through reflexion
version: 0.1.0
telemetry:
  expected_cadence: organic
  expected_participants: all
  health_signals:
    - "each active team member should have traces"
    - "0 reflexions in 14 days of active development is a red flag"
---
```

**Step 3: Update project-weekly-review frontmatter**

In `skills/reviews/project-weekly.md`, replace:

```yaml
---
name: project-weekly-review
description: Run weekly project review process
---
```

With:

```yaml
---
name: project-weekly-review
description: Run weekly project review process
version: 0.1.0
telemetry:
  expected_cadence: weekly
  expected_participants: at_least_one
  health_signals:
    - "should run every 7-10 days per project"
    - "gap > 14 days is unhealthy"
---
```

**Step 4: Update brainstorming-enhanced frontmatter**

In `skills/superpowers-enhanced/brainstorming-enhanced.md`, replace:

```yaml
---
name: brainstorming-enhanced
description: Enhanced brainstorming with ADR and mulch integration
---
```

With:

```yaml
---
name: brainstorming-enhanced
description: Enhanced brainstorming with ADR and mulch integration
version: 0.1.0
telemetry:
  expected_cadence: on_demand
  expected_participants: all
  health_signals:
    - "should precede any significant implementation work"
---
```

**Step 5: Update writing-plans-enhanced frontmatter**

In `skills/superpowers-enhanced/writing-plans-enhanced.md`, replace:

```yaml
---
name: writing-plans-enhanced
description: Enhanced plan writing with ADR and mulch integration
---
```

With:

```yaml
---
name: writing-plans-enhanced
description: Enhanced plan writing with ADR and mulch integration
version: 0.1.0
telemetry:
  expected_cadence: on_demand
  expected_participants: all
  health_signals:
    - "should follow brainstorming before implementation"
---
```

**Step 6: Verify all frontmatters parse**

Run: `source venv/bin/activate && python -c "
import yaml
for f in ['skills/adr/skill.md', 'skills/reflexion/capture.md', 'skills/reviews/project-weekly.md', 'skills/superpowers-enhanced/brainstorming-enhanced.md', 'skills/superpowers-enhanced/writing-plans-enhanced.md']:
    content = open(f).read()
    fm = yaml.safe_load(content.split('---', 2)[1])
    assert 'version' in fm, f'{f} missing version'
    assert 'telemetry' in fm, f'{f} missing telemetry'
    print(f'{f}: OK (v{fm[\"version\"]})')
"`

Expected: All 5 skills report OK

**Step 7: Commit**

```
feat(telemetry): add version and telemetry expectations to all skills
```

---

### Task 4: Add Telemetry Section to adr-author Skill

**Files:**
- Modify: `skills/adr/skill.md` (append before final section)

**Step 1: Add Telemetry section to end of skill**

Append the following after the last section ("## Example Invocations") at the end of `skills/adr/skill.md`:

```markdown

## Telemetry

After completing this workflow (whether successful, abandoned, or errored):

1. Check if `~/.tasty-dev/config.toml` exists and has `telemetry.enabled = true`
2. If disabled or missing, skip silently
3. If enabled, collect the following trace data:
   - Skill name, version, and mode (create/review/review-specific)
   - Project git remote and user identity
   - Step-level completion status for each workflow step executed
   - Outcome summary (ADRs created/reviewed, comments added, status changes)
   - Any issues (skipped steps, parse errors, user abandonment)
4. Write trace by piping JSON to `bin/write-telemetry-trace`:

```bash
echo '{"skill": "adr-author", "skill_version": "0.1.0", ...}' | bin/write-telemetry-trace
```

5. Do not let telemetry errors interrupt the user's workflow — if writing fails, continue silently

**What to capture in steps:**
- [completed] / [skipped] / [abandoned] status for each major step
- For creation mode: Steps 1-9, noting which were skipped or revised
- For review mode: queue building, each ADR reviewed, comments, approvals
- Critical analysis results (strength/contribution/consistency pass/fail)
- User actions at decision points (posted as-is, revised, cancelled)
```

**Step 2: Verify the section was added**

Run: `tail -20 skills/adr/skill.md` — should show the Telemetry section

**Step 3: Commit**

```
feat(telemetry): add telemetry instructions to adr-author skill
```

---

### Task 5: Add Telemetry Section to Remaining Skills

**Files:**
- Modify: `skills/reflexion/capture.md` (append at end)
- Modify: `skills/reviews/project-weekly.md` (append at end)

**Step 1: Add Telemetry section to reflexion-capture**

Append to end of `skills/reflexion/capture.md`:

```markdown

## Telemetry

After completing this workflow (whether successful, abandoned, or errored):

1. Check if `~/.tasty-dev/config.toml` exists and has `telemetry.enabled = true`
2. If disabled or missing, skip silently
3. If enabled, collect trace data:
   - Skill name, version
   - Project git remote and user identity
   - Classification result (strategic/tactical)
   - Whether user was prompted or it was auto-triggered
   - Outcome (captured, dismissed, deferred)
4. Write trace by piping JSON to `bin/write-telemetry-trace`
5. Do not let telemetry errors interrupt the user's workflow
```

**Step 2: Add Telemetry section to project-weekly-review**

Append to end of `skills/reviews/project-weekly.md`:

```markdown

## Telemetry

After completing this workflow (whether successful, abandoned, or errored):

1. Check if `~/.tasty-dev/config.toml` exists and has `telemetry.enabled = true`
2. If disabled or missing, skip silently
3. If enabled, collect trace data:
   - Skill name, version
   - Project git remote and user identity
   - Steps completed (process queue, handle strategic, handle tactical, git trends, finalize drafts, sync)
   - Counts: reflexions processed, ADRs created/updated, mulch entries added
   - Issues or steps skipped
4. Write trace by piping JSON to `bin/write-telemetry-trace`
5. Do not let telemetry errors interrupt the user's workflow
```

**Step 3: Commit**

```
feat(telemetry): add telemetry instructions to reflexion and weekly review skills
```

---

### Task 6: Create Health Assessment Skill

**Files:**
- Create: `skills/health-assessment/skill.md`

**Step 1: Create the health assessment skill**

```markdown
---
name: health-assessment
description: Analyze telemetry traces to assess tasty-dev system health across projects and users (development-time only)
version: 0.1.0
---

# Health Assessment Skill

## Purpose

Development-time skill for the tasty-dev skill author. Reads collected telemetry traces and evaluates system health against expectations declared by each skill.

This skill is NOT deployed with the plugin. It lives in this repo for analyzing telemetry data.

## Usage

```bash
# Assess health across all projects (reads ~/.tasty-dev/telemetry/)
/health-assessment

# Assess a specific project
/health-assessment --project github.com-org-project-alpha

# Assess from an unzipped telemetry folder someone sent you
/health-assessment --path /tmp/alice-telemetry/
```

## Behavior

### Step 1: Locate Trace Data

Determine the telemetry directory:
- Default: `~/.tasty-dev/telemetry/`
- If `--path` provided: use that path
- If `--project` provided: filter to that project subdirectory

List all project directories and trace files found.

### Step 2: Load Skill Expectations

Read frontmatter from all skills in the tasty-dev suite to extract `telemetry` blocks:
- `skills/adr/skill.md`
- `skills/reflexion/capture.md`
- `skills/reviews/project-weekly.md`
- `skills/superpowers-enhanced/brainstorming-enhanced.md`
- `skills/superpowers-enhanced/writing-plans-enhanced.md`

Build a map of skill name → expected cadence, participants, health signals.

### Step 3: Parse Traces

For each trace file:
- Parse YAML frontmatter (skill, version, mode, project, user, timestamp)
- Parse step entries for completion status
- Parse issues section
- Build aggregated data:
  - Per skill: invocation count, unique users, modes used
  - Per user: which skills used, frequency
  - Per project: all of the above
  - Timeline: first trace, last trace, gaps

### Step 4: Evaluate Health Signals

For each skill's declared health signals:
- Evaluate the natural language signal against the aggregated data
- Classify as: Healthy, Warning, or Issue
- Provide evidence (counts, dates, user lists)

**Evaluation guidelines:**
- "should run every 7-10 days" → check gap between last trace and now
- "each active team member should have traces" → compare users in traces vs users in git log
- "at least 1 invocation per project per month" → check trace count in last 30 days
- Absence of ANY traces for a skill → Issue

### Step 5: Check for Cross-Skill Patterns

Look for system-level concerns:
- Skills that have never been invoked
- Users who only use some skills but not others
- Projects with no telemetry at all (forgot to enable?)
- Step-level patterns: are certain steps consistently skipped?
- Issue patterns: same issue recurring across invocations

### Step 6: Present Health Report

Format:

```
## System Health: {project or "all projects"}
Period: {first trace date} to {last trace date} ({N} days)
Users: {list of unique users across traces}

### Healthy
- {skill}: {evidence of healthy usage}

### Warnings
- {skill}: {signal violated, evidence}

### Issues
- {skill}: {signal violated, evidence}

### Cross-Skill Observations
- {pattern observed}

### Recommendations
- {actionable suggestion for skill author}
```

## Notes

- This skill interprets health signals as natural language — use judgment, not rigid parsing
- When data is insufficient to evaluate a signal, say so rather than guessing
- Compare against git log for user activity when checking participation signals
- Trace files use YAML frontmatter — parse with a YAML library, not regex
```

**Step 2: Commit**

```
feat(telemetry): create health assessment skill for analyzing traces
```

---

### Task 7: Register Health Assessment in SKILL.md

**Files:**
- Modify: `SKILL.md`

**Step 1: Add health-assessment command**

Add after the `adr-author` section in `SKILL.md`:

```markdown
### `health-assessment`
Analyze telemetry traces to assess tasty-dev system health (development-time only).

**Trigger**: Use when validating skill effectiveness across projects and users, or when reviewing collected telemetry.

**Skill**: `health-assessment/skill`

**Modes**:
- `/health-assessment` — Assess all projects
- `/health-assessment --project <slug>` — Assess one project
- `/health-assessment --path <dir>` — Assess from an unzipped telemetry folder
```

**Step 2: Commit**

```
feat(telemetry): register health-assessment skill in SKILL.md
```

---

### Task 8: Add Telemetry Test for Existing Skill Tests

Verify that the adr-author template tests still pass and that skill frontmatters are valid with the new telemetry fields.

**Files:**
- Create: `tests/test_skill_telemetry.py`

**Step 1: Write tests**

```python
# tests/test_skill_telemetry.py
"""Tests for skill telemetry declarations."""
from pathlib import Path

import yaml


SKILL_FILES = [
    Path("skills/adr/skill.md"),
    Path("skills/reflexion/capture.md"),
    Path("skills/reviews/project-weekly.md"),
    Path("skills/superpowers-enhanced/brainstorming-enhanced.md"),
    Path("skills/superpowers-enhanced/writing-plans-enhanced.md"),
]


def _parse_frontmatter(path: Path) -> dict:
    """Extract and parse YAML frontmatter from skill file."""
    content = path.read_text()
    parts = content.split("---", 2)
    assert len(parts) >= 3, f"{path} must have YAML frontmatter"
    return yaml.safe_load(parts[1])


def test_all_skills_have_version():
    """Every skill declares a version in frontmatter."""
    for skill_path in SKILL_FILES:
        fm = _parse_frontmatter(skill_path)
        assert "version" in fm, f"{skill_path} missing 'version' field"


def test_all_skills_have_telemetry_block():
    """Every skill declares telemetry expectations."""
    for skill_path in SKILL_FILES:
        fm = _parse_frontmatter(skill_path)
        assert "telemetry" in fm, f"{skill_path} missing 'telemetry' block"
        telemetry = fm["telemetry"]
        assert "expected_cadence" in telemetry, f"{skill_path} missing expected_cadence"
        assert "expected_participants" in telemetry, f"{skill_path} missing expected_participants"
        assert "health_signals" in telemetry, f"{skill_path} missing health_signals"


def test_health_signals_are_non_empty():
    """Every skill has at least one health signal."""
    for skill_path in SKILL_FILES:
        fm = _parse_frontmatter(skill_path)
        signals = fm["telemetry"]["health_signals"]
        assert len(signals) > 0, f"{skill_path} has no health signals"


def test_expected_cadence_is_valid():
    """expected_cadence uses known values."""
    valid_cadences = {"weekly", "on_demand", "organic"}
    for skill_path in SKILL_FILES:
        fm = _parse_frontmatter(skill_path)
        cadence = fm["telemetry"]["expected_cadence"]
        assert cadence in valid_cadences, f"{skill_path} has invalid cadence: {cadence}"


def test_expected_participants_is_valid():
    """expected_participants uses known values."""
    valid_participants = {"all", "at_least_one"}
    for skill_path in SKILL_FILES:
        fm = _parse_frontmatter(skill_path)
        participants = fm["telemetry"]["expected_participants"]
        assert participants in valid_participants, f"{skill_path} has invalid participants: {participants}"
```

**Step 2: Run tests**

Run: `source venv/bin/activate && python -m pytest tests/test_skill_telemetry.py -v`
Expected: All 5 tests PASS

**Step 3: Commit**

```
test(telemetry): add tests for skill telemetry declarations
```

---

### Task 9: Run Full Test Suite and Final Verification

**Files:**
- Read: all modified files for consistency check

**Step 1: Run all tests**

Run: `source venv/bin/activate && python -m pytest tests/ -v`
Expected: All tests pass (existing + new)

**Step 2: Verify no skill is missing telemetry**

Run: `grep -L "telemetry:" skills/*/skill.md skills/*/*.md 2>/dev/null | grep -v TESTING | grep -v health-assessment`
Expected: No output (all skills have telemetry, health-assessment excluded since it's the consumer not producer)

**Step 3: Verify bin scripts are executable**

Run: `ls -la bin/init-user-config bin/write-telemetry-trace`
Expected: Both have execute permissions

**Step 4: End-to-end smoke test**

Run:
```bash
# Set up temp user dir
export TASTYDEV_USER_DIR=/tmp/telemetry-test
bin/init-user-config

# Enable telemetry
sed -i '' 's/enabled = false/enabled = true/' /tmp/telemetry-test/config.toml

# Write a test trace
echo '{"skill":"adr-author","skill_version":"0.1.0","tastydev_version":"0.1.0","mode":"review","project":"git@github.com:test/repo.git","user":"zac","steps":[{"status":"completed","description":"Test step","detail":"works"}],"outcome":["Test: 1"],"issues":[]}' | TASTYDEV_USER_DIR=/tmp/telemetry-test bin/write-telemetry-trace

# Verify trace exists
cat /tmp/telemetry-test/telemetry/github.com-test-repo/*.md

# Clean up
rm -rf /tmp/telemetry-test
```

Expected: Trace file created with correct frontmatter and structure

**Step 5: Commit**

```
feat(telemetry): complete telemetry infrastructure for tasty-dev skills
```
