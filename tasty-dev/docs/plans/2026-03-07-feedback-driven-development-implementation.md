# Feedback-Driven Development System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Claude Code plugin that captures development insights through reflexion loops, accumulates expertise in ADRs and mulch, and improves planning decisions over time.

**Architecture:** Plugin-based system with skills, commands, and hooks that integrate with existing superpowers. Uses ADRs for strategic decisions, mulch for tactical patterns, and knowledge repo for cross-project synthesis.

**Tech Stack:**
- Claude Code plugin system (YAML manifests)
- Python for CLI tools and utilities
- Markdown for ADRs and documentation
- Mulch CLI for tactical knowledge management
- Git for version control and sync

---

## Phase 1: Project Foundation

### Task 1: Initialize Plugin Structure

**Files:**
- Create: `plugin.yaml`
- Create: `README.md`
- Create: `skills/`
- Create: `hooks/`
- Create: `bin/`

**Step 1: Write test for plugin manifest validation**

```python
# tests/test_plugin_manifest.py
import yaml
import pytest
from pathlib import Path

def test_plugin_manifest_exists():
    """Plugin manifest file must exist"""
    manifest_path = Path("plugin.yaml")
    assert manifest_path.exists()

def test_plugin_manifest_valid_yaml():
    """Plugin manifest must be valid YAML"""
    with open("plugin.yaml") as f:
        manifest = yaml.safe_load(f)
    assert manifest is not None

def test_plugin_manifest_has_required_fields():
    """Plugin manifest must have name, version, description"""
    with open("plugin.yaml") as f:
        manifest = yaml.safe_load(f)
    assert "name" in manifest
    assert "version" in manifest
    assert "description" in manifest
    assert manifest["name"] == "tasty-dev"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_plugin_manifest.py -v`
Expected: FAIL with "No such file or directory: 'plugin.yaml'"

**Step 3: Create plugin manifest**

```yaml
# plugin.yaml
name: tasty-dev
version: 0.1.0
description: Feedback-driven development system with reflexion loops, ADRs, and cross-project learning

commands:
  - name: reflect
    description: Capture a development insight or decision
    skill: reflexion/capture

  - name: correct
    description: Correct a previous decision or pattern
    skill: reflexion/correct

  - name: review-project
    description: Run weekly project review
    skill: reviews/project-weekly

  - name: review-knowledge
    description: Run weekly knowledge repo review
    skill: reviews/knowledge-weekly

hooks:
  - name: reflexion-trigger-detector
    events: [tool_result, user_message]
    script: hooks/detect_reflexion_triggers.py

  - name: weekly-review-nudge
    events: [session_start, task_complete]
    script: hooks/nudge_weekly_review.py

skills_directory: skills
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_plugin_manifest.py -v`
Expected: PASS

**Step 5: Create directory structure**

```bash
mkdir -p skills/reflexion
mkdir -p skills/adr
mkdir -p skills/reviews
mkdir -p skills/superpowers-enhanced
mkdir -p hooks
mkdir -p bin
mkdir -p tests
```

**Step 6: Commit**

```bash
git add plugin.yaml README.md tests/test_plugin_manifest.py
git commit -m "feat: initialize tasty-dev plugin structure"
```

---

### Task 2: Setup Project Storage Structure

**Files:**
- Create: `bin/init-project-storage`
- Test: `tests/test_project_storage.py`

**Step 1: Write test for project storage initialization**

```python
# tests/test_project_storage.py
import subprocess
import tempfile
from pathlib import Path

def test_init_project_storage_creates_directories():
    """init-project-storage creates required directories"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        result = subprocess.run(
            ["bin/init-project-storage", str(project_path)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert (project_path / ".tasty-dev").exists()
        assert (project_path / ".tasty-dev" / "adr").exists()
        assert (project_path / ".tasty-dev" / "mulch").exists()
        assert (project_path / ".tasty-dev" / "queue").exists()
        assert (project_path / ".tasty-dev" / "config.yaml").exists()

def test_init_project_storage_creates_config():
    """init-project-storage creates valid config"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        config_path = project_path / ".tasty-dev" / "config.yaml"
        with open(config_path) as f:
            import yaml
            config = yaml.safe_load(f)

        assert "knowledge_repo" in config
        assert "last_project_review" in config
        assert config["last_project_review"] is None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_project_storage.py -v`
Expected: FAIL with "No such file or directory: 'bin/init-project-storage'"

**Step 3: Implement init-project-storage script**

```python
#!/usr/bin/env python3
# bin/init-project-storage
"""Initialize .tasty-dev storage structure in a project"""
import sys
from pathlib import Path
import yaml
from datetime import datetime

def init_project_storage(project_path: Path) -> None:
    """Create .tasty-dev directory structure"""
    tasty_dev_dir = project_path / ".tasty-dev"
    tasty_dev_dir.mkdir(exist_ok=True)

    # Create subdirectories
    (tasty_dev_dir / "adr").mkdir(exist_ok=True)
    (tasty_dev_dir / "mulch").mkdir(exist_ok=True)
    (tasty_dev_dir / "queue").mkdir(exist_ok=True)

    # Create config
    config = {
        "knowledge_repo": None,
        "last_project_review": None,
        "last_knowledge_review": None,
    }

    config_path = tasty_dev_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"Initialized .tasty-dev in {project_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: init-project-storage <project-path>")
        sys.exit(1)

    project_path = Path(sys.argv[1])
    init_project_storage(project_path)
```

**Step 4: Make script executable and run test**

Run: `chmod +x bin/init-project-storage && pytest tests/test_project_storage.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add bin/init-project-storage tests/test_project_storage.py
git commit -m "feat: add project storage initialization script"
```

---

## Phase 2: Core Reflexion Loop

### Task 3: Reflexion Trigger Detection Hook

**Files:**
- Create: `hooks/detect_reflexion_triggers.py`
- Test: `tests/test_reflexion_triggers.py`

**Step 1: Write test for trigger detection**

```python
# tests/test_reflexion_triggers.py
import pytest
from hooks.detect_reflexion_triggers import (
    detect_trigger,
    TriggerType,
    TriggerEvent
)

def test_detect_human_deliberation():
    """Detects human deliberation in user messages"""
    user_message = "Actually, I think we should use PostgreSQL instead"
    trigger = detect_trigger("user_message", {"content": user_message})

    assert trigger is not None
    assert trigger.type == TriggerType.HUMAN_DELIBERATION
    assert "PostgreSQL" in trigger.context

def test_detect_test_failure():
    """Detects test failures in tool results"""
    tool_result = {
        "tool": "Bash",
        "command": "pytest tests/",
        "output": "FAILED tests/test_api.py::test_endpoint",
        "exit_code": 1
    }
    trigger = detect_trigger("tool_result", tool_result)

    assert trigger is not None
    assert trigger.type == TriggerType.SYSTEM_FAILURE
    assert "test_endpoint" in trigger.context

def test_no_trigger_for_simple_acceptance():
    """No trigger for simple acceptance messages"""
    user_message = "Great, thanks!"
    trigger = detect_trigger("user_message", {"content": user_message})

    assert trigger is None

def test_detect_design_conflict():
    """Detects conflicts with existing ADRs"""
    user_message = "Wait, that conflicts with our decision to use REST"
    trigger = detect_trigger("user_message", {"content": user_message})

    assert trigger is not None
    assert trigger.type == TriggerType.DESIGN_CONFLICT
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_reflexion_triggers.py -v`
Expected: FAIL with "No module named 'hooks.detect_reflexion_triggers'"

**Step 3: Implement trigger detection**

```python
# hooks/detect_reflexion_triggers.py
"""Detect reflexion triggers from user messages and tool results"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
import re

class TriggerType(Enum):
    HUMAN_DELIBERATION = "human_deliberation"
    SYSTEM_FAILURE = "system_failure"
    DESIGN_CONFLICT = "design_conflict"
    REPEATED_FRICTION = "repeated_friction"
    USER_INVOCATION = "user_invocation"

@dataclass
class TriggerEvent:
    type: TriggerType
    context: str
    severity: str  # "major" or "minor"

# Patterns for human deliberation
DELIBERATION_PATTERNS = [
    r"\b(actually|instead|rather|alternatively)\b",
    r"\b(think|consider|prefer|suggest)\b.*\b(should|could|might)\b",
    r"\b(what about|how about|why not)\b",
    r"\b(but|however|although)\b",
    r"\b(option|alternative|approach)\b",
]

# Patterns for design conflicts
CONFLICT_PATTERNS = [
    r"\b(conflict|contradicts?|violates?)\b",
    r"\b(against|breaks|challenges)\b.*\b(decision|ADR|architecture)\b",
    r"\bwait\b.*\b(that|this)\b",
]

def detect_trigger(event_type: str, event_data: Dict[str, Any]) -> Optional[TriggerEvent]:
    """Detect if event should trigger reflexion"""

    if event_type == "user_message":
        return _detect_user_message_trigger(event_data)
    elif event_type == "tool_result":
        return _detect_tool_result_trigger(event_data)

    return None

def _detect_user_message_trigger(data: Dict[str, Any]) -> Optional[TriggerEvent]:
    """Detect triggers in user messages"""
    content = data.get("content", "").lower()

    # Skip simple acceptance messages
    if re.match(r"^(ok|okay|great|thanks|sure|yes|yep|yeah)[\s!.]*$", content):
        return None

    # Check for explicit commands
    if re.match(r"/(reflect|correct)", content):
        return TriggerEvent(
            type=TriggerType.USER_INVOCATION,
            context=content,
            severity="major"
        )

    # Check for design conflicts
    for pattern in CONFLICT_PATTERNS:
        if re.search(pattern, content):
            return TriggerEvent(
                type=TriggerType.DESIGN_CONFLICT,
                context=content,
                severity="major"
            )

    # Check for deliberation
    for pattern in DELIBERATION_PATTERNS:
        if re.search(pattern, content):
            return TriggerEvent(
                type=TriggerType.HUMAN_DELIBERATION,
                context=content,
                severity="minor"
            )

    return None

def _detect_tool_result_trigger(data: Dict[str, Any]) -> Optional[TriggerEvent]:
    """Detect triggers in tool results"""
    tool = data.get("tool", "")
    output = data.get("output", "").lower()
    exit_code = data.get("exit_code", 0)

    # Test failures
    if tool == "Bash" and exit_code != 0:
        if any(word in output for word in ["failed", "error", "failure"]):
            return TriggerEvent(
                type=TriggerType.SYSTEM_FAILURE,
                context=output[:200],
                severity="major"
            )

    return None
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_reflexion_triggers.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add hooks/detect_reflexion_triggers.py tests/test_reflexion_triggers.py
git commit -m "feat: add reflexion trigger detection"
```

---

### Task 4: Reflexion Capture Skill

**Files:**
- Create: `skills/reflexion/capture.md`
- Create: `bin/capture-reflexion`
- Test: `tests/test_reflexion_capture.py`

**Step 1: Write test for reflexion capture**

```python
# tests/test_reflexion_capture.py
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime

def test_capture_reflexion_creates_queue_entry():
    """Capture creates entry in reflexion queue"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        reflexion_data = {
            "context": "Adding API endpoint",
            "initial_suggestion": "Use REST",
            "alternatives": ["GraphQL", "gRPC"],
            "friction": "User prefers GraphQL",
            "resolution": "Switch to GraphQL",
            "why": "Better for our use case with nested data"
        }

        result = subprocess.run(
            ["bin/capture-reflexion", str(project_path)],
            input=json.dumps(reflexion_data),
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        queue_dir = project_path / ".tasty-dev" / "queue"
        queue_files = list(queue_dir.glob("*.json"))
        assert len(queue_files) == 1

        with open(queue_files[0]) as f:
            saved = json.load(f)

        assert saved["context"] == reflexion_data["context"]
        assert saved["resolution"] == reflexion_data["resolution"]
        assert "timestamp" in saved
        assert "classification" in saved

def test_capture_reflexion_infers_classification():
    """Capture infers strategic vs tactical classification"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        # Strategic decision (architecture change)
        strategic_data = {
            "context": "Database selection",
            "initial_suggestion": "SQLite",
            "friction": "Need distributed transactions",
            "resolution": "Use PostgreSQL with two-phase commit",
            "why": "Required for our distributed architecture"
        }

        subprocess.run(
            ["bin/capture-reflexion", str(project_path)],
            input=json.dumps(strategic_data),
            text=True
        )

        queue_files = list((project_path / ".tasty-dev" / "queue").glob("*.json"))
        with open(queue_files[0]) as f:
            saved = json.load(f)

        assert saved["classification"]["level"] == "strategic"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_reflexion_capture.py -v`
Expected: FAIL with "No such file or directory: 'bin/capture-reflexion'"

**Step 3: Implement capture-reflexion script**

```python
#!/usr/bin/env python3
# bin/capture-reflexion
"""Capture a reflexion and add to queue"""
import sys
import json
from pathlib import Path
from datetime import datetime
import re

def infer_classification(reflexion: dict) -> dict:
    """Infer strategic vs tactical classification"""
    context = reflexion.get("context", "").lower()
    resolution = reflexion.get("resolution", "").lower()
    why = reflexion.get("why", "").lower()

    combined = f"{context} {resolution} {why}"

    # Strategic keywords
    strategic_keywords = [
        "architecture", "database", "framework", "design pattern",
        "distributed", "microservices", "monolith", "api design",
        "security model", "authentication", "authorization", "scalability"
    ]

    # Tactical keywords
    tactical_keywords = [
        "test pattern", "naming convention", "code style",
        "configuration", "utility function", "helper", "formatting"
    ]

    strategic_score = sum(1 for kw in strategic_keywords if kw in combined)
    tactical_score = sum(1 for kw in tactical_keywords if kw in combined)

    if strategic_score > tactical_score:
        level = "strategic"
    else:
        level = "tactical"

    # Scope inference (simplified)
    scope = "project-specific"
    if any(word in combined for word in ["always", "general", "universal"]):
        scope = "potentially-universal"

    return {
        "level": level,
        "scope": scope,
        "confidence": "low"  # Will be validated in weekly review
    }

def capture_reflexion(project_path: Path, reflexion_data: dict) -> None:
    """Capture reflexion and add to queue"""
    queue_dir = project_path / ".tasty-dev" / "queue"
    queue_dir.mkdir(parents=True, exist_ok=True)

    # Add metadata
    reflexion_data["timestamp"] = datetime.now().isoformat()
    reflexion_data["classification"] = infer_classification(reflexion_data)
    reflexion_data["status"] = "pending"

    # Save to queue
    filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    queue_file = queue_dir / filename

    with open(queue_file, "w") as f:
        json.dump(reflexion_data, f, indent=2)

    print(f"Captured reflexion: {filename}")
    print(f"Classification: {reflexion_data['classification']['level']}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: capture-reflexion <project-path>")
        print("Reads reflexion data from stdin as JSON")
        sys.exit(1)

    project_path = Path(sys.argv[1])
    reflexion_data = json.load(sys.stdin)

    capture_reflexion(project_path, reflexion_data)
```

**Step 4: Make executable and run test**

Run: `chmod +x bin/capture-reflexion && pytest tests/test_reflexion_capture.py -v`
Expected: PASS

**Step 5: Create capture skill**

```markdown
# skills/reflexion/capture.md
---
name: reflexion-capture
description: Capture a development insight or decision through reflexion
---

# Reflexion Capture

When a reflexion trigger is detected, capture the insight systematically.

## What to Capture

1. **Context** - What task/goal were we working on?
2. **Initial suggestion** - What did the agent propose?
3. **Alternatives considered** - What other options were discussed?
4. **Friction point** - What was the concern, failure, or discussion?
5. **Resolution** - What was decided? What happened?
6. **Why** - Rationale for resolution and why alternatives were rejected

## Process

**Step 1:** Acknowledge the trigger

"I notice we're deliberating about [topic]. Let me capture this for learning."

**Step 2:** Ask clarifying questions if needed

- What other approaches did you consider?
- Why is this approach better?
- Does this apply only to this project or more broadly?

**Step 3:** Capture using bin/capture-reflexion

```bash
echo '{
  "context": "...",
  "initial_suggestion": "...",
  "alternatives": ["..."],
  "friction": "...",
  "resolution": "...",
  "why": "..."
}' | bin/capture-reflexion .
```

**Step 4:** Inform user of classification

"Captured as [strategic/tactical]. Will be reviewed in next weekly review."

## Severity Handling

**Major triggers** (design conflicts, system failures):
- Capture immediately
- May pause for explicit decision

**Minor triggers** (small deliberations):
- Capture without interrupting flow
- Queue for weekly review
```

**Step 6: Commit**

```bash
git add bin/capture-reflexion tests/test_reflexion_capture.py skills/reflexion/capture.md
git commit -m "feat: add reflexion capture skill and tool"
```

---

### Task 5: ADR Creation Tool

**Files:**
- Create: `bin/create-adr`
- Create: `templates/adr-template.md`
- Test: `tests/test_adr_creation.py`

**Step 1: Write test for ADR creation**

```python
# tests/test_adr_creation.py
import subprocess
import tempfile
from pathlib import Path

def test_create_adr_generates_file():
    """create-adr generates numbered ADR file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        result = subprocess.run(
            ["bin/create-adr", str(project_path), "Use PostgreSQL for persistence"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        adr_dir = project_path / ".tasty-dev" / "adr"
        adr_files = list(adr_dir.glob("*.md"))

        assert len(adr_files) == 1
        assert "0001-use-postgresql-for-persistence" in adr_files[0].name

def test_create_adr_uses_template():
    """create-adr uses standard template"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        subprocess.run(
            ["bin/create-adr", str(project_path), "Use PostgreSQL"],
            capture_output=True
        )

        adr_files = list((project_path / ".tasty-dev" / "adr").glob("*.md"))
        with open(adr_files[0]) as f:
            content = f.read()

        assert "# Use PostgreSQL" in content
        assert "## Status" in content
        assert "## Context" in content
        assert "## Decision" in content
        assert "## Consequences" in content
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_adr_creation.py -v`
Expected: FAIL with "No such file or directory: 'bin/create-adr'"

**Step 3: Create ADR template**

```markdown
# templates/adr-template.md
# {title}

**Date:** {date}
**Status:** Draft

## Context

What is the issue that we're seeing that is motivating this decision or change?

## Decision

What is the change that we're proposing and/or doing?

## Alternatives Considered

What other approaches did we consider?

- **Alternative 1:** Description and why it was rejected
- **Alternative 2:** Description and why it was rejected

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive

- Benefit 1
- Benefit 2

### Negative

- Trade-off 1
- Trade-off 2

## References

- Related ADRs:
- Related mulch records:
- External references:
```

**Step 4: Implement create-adr script**

```python
#!/usr/bin/env python3
# bin/create-adr
"""Create a new ADR from template"""
import sys
from pathlib import Path
from datetime import datetime
import re

def slugify(text: str) -> str:
    """Convert title to slug"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text

def get_next_adr_number(adr_dir: Path) -> int:
    """Get next ADR number"""
    existing = list(adr_dir.glob("*.md"))
    if not existing:
        return 1

    numbers = []
    for path in existing:
        match = re.match(r'(\d+)-', path.name)
        if match:
            numbers.append(int(match.group(1)))

    return max(numbers, default=0) + 1

def create_adr(project_path: Path, title: str) -> Path:
    """Create new ADR file"""
    adr_dir = project_path / ".tasty-dev" / "adr"
    adr_dir.mkdir(parents=True, exist_ok=True)

    # Get template
    template_path = Path(__file__).parent.parent / "templates" / "adr-template.md"
    with open(template_path) as f:
        template = f.read()

    # Fill template
    content = template.format(
        title=title,
        date=datetime.now().strftime("%Y-%m-%d")
    )

    # Create filename
    number = get_next_adr_number(adr_dir)
    slug = slugify(title)
    filename = f"{number:04d}-{slug}.md"
    adr_path = adr_dir / filename

    with open(adr_path, "w") as f:
        f.write(content)

    print(f"Created ADR: {filename}")
    return adr_path

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: create-adr <project-path> <title>")
        sys.exit(1)

    project_path = Path(sys.argv[1])
    title = sys.argv[2]

    adr_path = create_adr(project_path, title)
    print(f"Edit: {adr_path}")
```

**Step 5: Make executable and run test**

Run: `chmod +x bin/create-adr && pytest tests/test_adr_creation.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add bin/create-adr templates/adr-template.md tests/test_adr_creation.py
git commit -m "feat: add ADR creation tool with template"
```

---

## Phase 3: Weekly Review System

### Task 6: Project Weekly Review Skill

**Files:**
- Create: `skills/reviews/project-weekly.md`
- Create: `bin/run-project-review`
- Test: `tests/test_project_review.py`

**Step 1: Write test for project review**

```python
# tests/test_project_review.py
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta

def test_project_review_processes_queue():
    """Project review processes reflexion queue"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        # Add some reflexions to queue
        queue_dir = project_path / ".tasty-dev" / "queue"
        reflexion = {
            "context": "API design",
            "resolution": "Use REST",
            "classification": {"level": "strategic", "scope": "project-specific"},
            "status": "pending"
        }

        with open(queue_dir / "20260307-120000.json", "w") as f:
            json.dump(reflexion, f)

        result = subprocess.run(
            ["bin/run-project-review", str(project_path)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "processed" in result.stdout.lower()

def test_project_review_updates_last_review_date():
    """Project review updates config with last review date"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        subprocess.run(["bin/run-project-review", str(project_path)])

        config_path = project_path / ".tasty-dev" / "config.yaml"
        with open(config_path) as f:
            import yaml
            config = yaml.safe_load(f)

        assert config["last_project_review"] is not None
        review_date = datetime.fromisoformat(config["last_project_review"])
        assert (datetime.now() - review_date).total_seconds() < 60
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_project_review.py -v`
Expected: FAIL with "No such file or directory: 'bin/run-project-review'"

**Step 3: Implement project review script**

```python
#!/usr/bin/env python3
# bin/run-project-review
"""Run weekly project review"""
import sys
from pathlib import Path
from datetime import datetime
import json
import yaml

def process_queue(project_path: Path) -> list:
    """Process reflexion queue"""
    queue_dir = project_path / ".tasty-dev" / "queue"
    pending_items = []

    for queue_file in queue_dir.glob("*.json"):
        with open(queue_file) as f:
            reflexion = json.load(f)

        if reflexion.get("status") == "pending":
            pending_items.append({
                "file": queue_file,
                "data": reflexion
            })

    return pending_items

def update_last_review(project_path: Path) -> None:
    """Update last review timestamp"""
    config_path = project_path / ".tasty-dev" / "config.yaml"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    config["last_project_review"] = datetime.now().isoformat()

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

def run_project_review(project_path: Path) -> None:
    """Run weekly project review"""
    print("=" * 60)
    print("PROJECT WEEKLY REVIEW")
    print("=" * 60)

    # Process queue
    print("\n1. Processing reflexion queue...")
    pending = process_queue(project_path)
    print(f"   Found {len(pending)} pending reflexions")

    if pending:
        print("\n   Items to review:")
        for item in pending:
            data = item["data"]
            print(f"   - {data.get('context', 'Unknown')}")
            print(f"     Classification: {data['classification']['level']}")
            print(f"     Resolution: {data.get('resolution', 'Unknown')[:60]}...")

    # Update timestamp
    update_last_review(project_path)
    print(f"\n✓ Review complete. Processed {len(pending)} items.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: run-project-review <project-path>")
        sys.exit(1)

    project_path = Path(sys.argv[1])
    run_project_review(project_path)
```

**Step 4: Make executable and run test**

Run: `chmod +x bin/run-project-review && pytest tests/test_project_review.py -v`
Expected: PASS

**Step 5: Create project review skill**

```markdown
# skills/reviews/project-weekly.md
---
name: project-weekly-review
description: Run weekly project review process
---

# Project Weekly Review

**Cadence:** Weekly per project (different schedules per project)

**When to use:** Invoked by `/review-project` command or weekly nudge

## Process

### Step 1: Process Reflexion Queue

Review all pending reflexions captured during the week:

```bash
bin/run-project-review .
```

For each reflexion:

1. **Validate classification** - Is it strategic or tactical?
2. **Validate scope** - Project-specific or potentially universal?
3. **Decide routing:**
   - Strategic → Create or update ADR
   - Tactical → Add to mulch

### Step 2: Handle Strategic Reflexions

For strategic items:

```bash
bin/create-adr . "Title from reflexion"
```

Fill in the ADR with:
- Context from reflexion
- Decision (resolution)
- Alternatives considered
- Consequences

Mark reflexion as `processed` in queue.

### Step 3: Handle Tactical Reflexions

For tactical items, add to mulch:

```bash
cd .tasty-dev/mulch
ml add domain "Pattern description" \
  --context "Context from reflexion" \
  --why "Why from reflexion"
```

Mark reflexion as `processed` in queue.

### Step 4: Git Trend Analysis

Review recent commits for patterns:

```bash
git log --since="1 week ago" --oneline
git diff --stat HEAD~7..HEAD
```

Look for:
- Repeated modifications to same files
- Common error patterns
- Emerging conventions

### Step 5: Finalize Draft ADRs

Review any ADRs with status "Draft":

```bash
ls .tasty-dev/adr/*.md
```

Update status to "Accepted" when ready.

### Step 6: Sync to Knowledge Repo

If knowledge repo configured:

```bash
# Push project's mulch and ADRs
# Pull universal updates
# (Implementation in Phase 4)
```

## Enforcement

**Gentle reminders:**
- Day 7: "It's been a week since last project review"
- Day 10+: More prominent reminder at session start

**Never blocks work**, but keeps reviews from slipping indefinitely.
```

**Step 6: Commit**

```bash
git add bin/run-project-review skills/reviews/project-weekly.md tests/test_project_review.py
git commit -m "feat: add project weekly review system"
```

---

## Phase 4: Superpowers Integration

### Task 7: Enhanced Brainstorming Skill

**Files:**
- Create: `skills/superpowers-enhanced/brainstorming-enhanced.md`
- Create: `bin/query-adr`
- Test: `tests/test_adr_query.py`

**Step 1: Write test for ADR querying**

```python
# tests/test_adr_query.py
import subprocess
import tempfile
from pathlib import Path

def test_query_adr_finds_relevant():
    """query-adr finds relevant ADRs by topic"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        # Create some ADRs
        adr_dir = project_path / ".tasty-dev" / "adr"

        adr1 = adr_dir / "0001-use-postgresql.md"
        adr1.write_text("""# Use PostgreSQL for Persistence
## Context
Need database for application data.
## Decision
Use PostgreSQL with connection pooling.
""")

        adr2 = adr_dir / "0002-use-rest-api.md"
        adr2.write_text("""# Use REST API
## Context
Need API for frontend communication.
## Decision
Use REST with OpenAPI specification.
""")

        result = subprocess.run(
            ["bin/query-adr", str(project_path), "database"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "postgresql" in result.stdout.lower()
        assert "rest" not in result.stdout.lower()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_adr_query.py -v`
Expected: FAIL with "No such file or directory: 'bin/query-adr'"

**Step 3: Implement query-adr script**

```python
#!/usr/bin/env python3
# bin/query-adr
"""Query ADRs by topic"""
import sys
from pathlib import Path
import re

def search_adr(adr_path: Path, query: str) -> dict:
    """Search ADR content for query terms"""
    with open(adr_path) as f:
        content = f.read()

    query_lower = query.lower()
    content_lower = content.lower()

    # Simple scoring: count occurrences
    score = content_lower.count(query_lower)

    # Extract title
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else adr_path.stem

    return {
        "path": adr_path,
        "title": title,
        "score": score,
        "excerpt": content[:200]
    }

def query_adrs(project_path: Path, query: str) -> list:
    """Query all ADRs and return relevant ones"""
    adr_dir = project_path / ".tasty-dev" / "adr"

    if not adr_dir.exists():
        return []

    results = []
    for adr_file in adr_dir.glob("*.md"):
        result = search_adr(adr_file, query)
        if result["score"] > 0:
            results.append(result)

    # Sort by relevance
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: query-adr <project-path> <query>")
        sys.exit(1)

    project_path = Path(sys.argv[1])
    query = sys.argv[2]

    results = query_adrs(project_path, query)

    if not results:
        print(f"No ADRs found for query: {query}")
        sys.exit(0)

    print(f"Found {len(results)} relevant ADR(s):\n")
    for result in results:
        print(f"📄 {result['title']}")
        print(f"   {result['path'].name}")
        print(f"   Relevance: {result['score']}")
        print()
```

**Step 4: Make executable and run test**

Run: `chmod +x bin/query-adr && pytest tests/test_adr_query.py -v`
Expected: PASS

**Step 5: Create enhanced brainstorming skill**

```markdown
# skills/superpowers-enhanced/brainstorming-enhanced.md
---
name: brainstorming-enhanced
description: Enhanced brainstorming with ADR and mulch integration
---

# Enhanced Brainstorming with Feedback Loop

This enhances the superpowers brainstorming skill with ADR and mulch integration.

**When to use:** When starting creative work - creating features, building components, adding functionality

## Integration with Standard Brainstorming

**Step 0:** Query ADRs first

Before starting brainstorming, query relevant ADRs:

```bash
bin/query-adr . "<topic-keywords>"
```

Load relevant ADRs to understand:
- Strategic decisions already made
- Boundaries and constraints
- Approved patterns and approaches

**During brainstorming:**

1. **Align with ADRs** - Ensure proposals respect existing decisions
2. **Surface conflicts explicitly** - If ADR doesn't fit, trigger reflexion
3. **Reference ADRs** - Note which ADRs informed the design

**After brainstorming:**

If new strategic decisions emerged:
1. Trigger reflexion capture for major decisions
2. Queue for ADR creation in next weekly review

## ADR Conflict Handling

If implementation idea conflicts with ADR:

**Major conflict (blocks progress):**
1. Pause immediately
2. Present conflict to user explicitly
3. Options: Update ADR, change approach, or document exception
4. Capture reflexion with high priority

**Minor tension:**
1. Flag the tension
2. Continue with current ADR guidance
3. Queue reflexion for weekly review

## Example Integration

User: "Let's add a new API endpoint for user profiles"

Agent:
1. Query ADRs for "API", "endpoints", "users"
2. Find ADR-0005: "Use REST with OpenAPI spec"
3. Find ADR-0012: "User data requires authentication"
4. Brainstorm with those constraints
5. Ensure design aligns with existing decisions
6. Reference ADRs in design document
```

**Step 6: Commit**

```bash
git add bin/query-adr skills/superpowers-enhanced/brainstorming-enhanced.md tests/test_adr_query.py
git commit -m "feat: add ADR querying and enhanced brainstorming"
```

---

### Task 8: Enhanced Writing Plans Skill

**Files:**
- Create: `skills/superpowers-enhanced/writing-plans-enhanced.md`
- Create: `bin/query-mulch`
- Test: `tests/test_mulch_query.py`

**Step 1: Write test for mulch querying**

```python
# tests/test_mulch_query.py
import subprocess
import tempfile
from pathlib import Path

def test_query_mulch_integration():
    """query-mulch integrates with mulch CLI"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        # This test assumes mulch CLI is installed
        # Skip if not available
        check = subprocess.run(
            ["which", "ml"],
            capture_output=True
        )

        if check.returncode != 0:
            import pytest
            pytest.skip("mulch CLI not installed")

        # Query should work even with empty mulch
        result = subprocess.run(
            ["bin/query-mulch", str(project_path), "testing"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_mulch_query.py -v`
Expected: FAIL or SKIP

**Step 3: Implement query-mulch script**

```python
#!/usr/bin/env python3
# bin/query-mulch
"""Query mulch records by domain/topic"""
import sys
import subprocess
from pathlib import Path

def query_mulch(project_path: Path, query: str) -> str:
    """Query mulch using ml CLI"""
    mulch_dir = project_path / ".tasty-dev" / "mulch"

    if not mulch_dir.exists():
        return "No mulch records found"

    # Use mulch CLI to search
    try:
        result = subprocess.run(
            ["ml", "search", query],
            cwd=mulch_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Mulch query failed: {e.stderr}"
    except FileNotFoundError:
        return "Mulch CLI not installed. Install from: https://github.com/your-repo/mulch"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: query-mulch <project-path> <query>")
        sys.exit(1)

    project_path = Path(sys.argv[1])
    query = sys.argv[2]

    results = query_mulch(project_path, query)
    print(results)
```

**Step 4: Make executable and run test**

Run: `chmod +x bin/query-mulch && pytest tests/test_mulch_query.py -v`
Expected: PASS or SKIP

**Step 5: Create enhanced writing plans skill**

```markdown
# skills/superpowers-enhanced/writing-plans-enhanced.md
---
name: writing-plans-enhanced
description: Enhanced plan writing with ADR and mulch integration
---

# Enhanced Writing Plans with Accumulated Expertise

This enhances the superpowers writing-plans skill with comprehensive knowledge integration.

**When to use:** When writing implementation plans after brainstorming

## Integration with Standard Plan Writing

**Before writing plan:**

Query both ADRs and mulch extensively:

```bash
# Strategic context
bin/query-adr . "<feature-area>"
bin/query-adr . "<technology>"

# Tactical patterns
bin/query-mulch . "<domain>"
bin/query-mulch . "testing"
bin/query-mulch . "<language>"
```

**Load accumulated expertise:**
- ADRs inform architecture decisions
- Mulch informs implementation details
- Test patterns from mulch
- Configuration patterns from mulch
- Known edge cases from mulch

**During plan writing:**

1. **Every task informed by expertise** - Not just breadcrumbs, full integration
2. **Test patterns** - Use project-specific test patterns from mulch
3. **Configuration** - Reference mulch for setup patterns
4. **Edge cases** - Include known gotchas from mulch
5. **File paths** - Use established project structure

**In plan document:**

Add section after header:

```markdown
## Relevant Knowledge

**ADRs Referenced:**
- ADR-0005: Use REST with OpenAPI spec
- ADR-0012: User data requires authentication

**Mulch Patterns:**
- `testing/api-integration-tests` - Integration test setup
- `config/database-pooling` - DB connection config
- `patterns/error-handling` - Standard error handling

---
```

## Unknown Areas

If plan reveals unknown areas:

1. **Flag explicitly** - "No mulch pattern found for X"
2. **Research** - Agent investigates or asks user
3. **Document decision** - Capture for future mulch
4. **Continue** - Don't block on missing patterns

## Example Integration

Standard plan task:

```markdown
### Task 3: Implement User Endpoint

**Step 1: Write the failing test**

Use project's API test pattern (from mulch `testing/api-integration-tests`):

\`\`\`python
# tests/test_user_api.py
from tests.fixtures import api_client, auth_token

def test_get_user_profile(api_client, auth_token):
    response = api_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert "email" in response.json()
\`\`\`
```

Notice: Test uses established patterns, not generic examples.
```

**Step 6: Commit**

```bash
git add bin/query-mulch skills/superpowers-enhanced/writing-plans-enhanced.md tests/test_mulch_query.py
git commit -m "feat: add mulch querying and enhanced plan writing"
```

---

## Phase 5: Hook Integration

### Task 9: Weekly Review Nudge Hook

**Files:**
- Create: `hooks/nudge_weekly_review.py`
- Test: `tests/test_weekly_nudge.py`

**Step 1: Write test for weekly nudge**

```python
# tests/test_weekly_nudge.py
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import yaml
import subprocess

def test_nudge_when_review_overdue():
    """Hook nudges when review is overdue"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        # Set last review to 8 days ago
        config_path = project_path / ".tasty-dev" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

        config["last_project_review"] = (
            datetime.now() - timedelta(days=8)
        ).isoformat()

        with open(config_path, "w") as f:
            yaml.dump(config, f)

        # Run hook
        from hooks.nudge_weekly_review import check_review_needed
        result = check_review_needed(project_path)

        assert result is not None
        assert result["days_since"] == 8
        assert result["severity"] == "gentle"

def test_no_nudge_when_review_recent():
    """Hook doesn't nudge when review is recent"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        # Set last review to 2 days ago
        config_path = project_path / ".tasty-dev" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

        config["last_project_review"] = (
            datetime.now() - timedelta(days=2)
        ).isoformat()

        with open(config_path, "w") as f:
            yaml.dump(config, f)

        from hooks.nudge_weekly_review import check_review_needed
        result = check_review_needed(project_path)

        assert result is None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_weekly_nudge.py -v`
Expected: FAIL with "No module named 'hooks.nudge_weekly_review'"

**Step 3: Implement weekly nudge hook**

```python
# hooks/nudge_weekly_review.py
"""Hook to nudge for weekly project review"""
from pathlib import Path
from datetime import datetime, timedelta
import yaml
from typing import Optional, Dict

def check_review_needed(project_path: Path) -> Optional[Dict]:
    """Check if weekly review is needed"""
    config_path = project_path / ".tasty-dev" / "config.yaml"

    if not config_path.exists():
        return None

    with open(config_path) as f:
        config = yaml.safe_load(f)

    last_review = config.get("last_project_review")

    if last_review is None:
        # Never reviewed
        return {
            "days_since": None,
            "severity": "gentle",
            "message": "Consider running your first project review: /review-project"
        }

    last_review_date = datetime.fromisoformat(last_review)
    days_since = (datetime.now() - last_review_date).days

    if days_since >= 10:
        return {
            "days_since": days_since,
            "severity": "prominent",
            "message": f"⚠️  Weekly review overdue by {days_since - 7} days. Run: /review-project"
        }
    elif days_since >= 7:
        return {
            "days_since": days_since,
            "severity": "gentle",
            "message": f"💡 It's been {days_since} days since your last project review. Run: /review-project"
        }

    return None

def main():
    """Hook entry point"""
    # Called by Claude Code hook system
    # Event data passed via stdin or environment

    # For now, check current directory
    project_path = Path.cwd()
    result = check_review_needed(project_path)

    if result:
        print(result["message"])

if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_weekly_nudge.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add hooks/nudge_weekly_review.py tests/test_weekly_nudge.py
git commit -m "feat: add weekly review nudge hook"
```

---

## Phase 6: Documentation and Testing

### Task 10: Integration Tests

**Files:**
- Create: `tests/test_integration_workflow.py`

**Step 1: Write integration test**

```python
# tests/test_integration_workflow.py
"""Integration tests for complete workflow"""
import subprocess
import tempfile
from pathlib import Path
import json
import yaml

def test_complete_reflexion_workflow():
    """Test complete workflow from trigger to ADR"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Step 1: Initialize project
        result = subprocess.run(
            ["bin/init-project-storage", str(project_path)],
            capture_output=True
        )
        assert result.returncode == 0

        # Step 2: Capture a reflexion
        reflexion = {
            "context": "API design decision",
            "initial_suggestion": "Use GraphQL",
            "alternatives": ["REST", "gRPC"],
            "friction": "User prefers REST for simplicity",
            "resolution": "Use REST with OpenAPI",
            "why": "Team familiarity and tooling ecosystem"
        }

        result = subprocess.run(
            ["bin/capture-reflexion", str(project_path)],
            input=json.dumps(reflexion),
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

        # Step 3: Verify queue entry
        queue_dir = project_path / ".tasty-dev" / "queue"
        queue_files = list(queue_dir.glob("*.json"))
        assert len(queue_files) == 1

        with open(queue_files[0]) as f:
            saved = json.load(f)
        assert saved["classification"]["level"] == "strategic"

        # Step 4: Run project review
        result = subprocess.run(
            ["bin/run-project-review", str(project_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

        # Step 5: Create ADR from reflexion
        result = subprocess.run(
            ["bin/create-adr", str(project_path), "Use REST API"],
            capture_output=True
        )
        assert result.returncode == 0

        # Step 6: Verify ADR exists
        adr_files = list((project_path / ".tasty-dev" / "adr").glob("*.md"))
        assert len(adr_files) == 1

        # Step 7: Query ADR
        result = subprocess.run(
            ["bin/query-adr", str(project_path), "API"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "rest" in result.stdout.lower()

def test_adr_query_workflow():
    """Test ADR querying during design"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        # Create some ADRs
        subprocess.run(["bin/create-adr", str(project_path), "Use PostgreSQL"])
        subprocess.run(["bin/create-adr", str(project_path), "Use REST API"])
        subprocess.run(["bin/create-adr", str(project_path), "Use JWT Auth"])

        # Query for database decisions
        result = subprocess.run(
            ["bin/query-adr", str(project_path), "database"],
            capture_output=True,
            text=True
        )

        assert "postgresql" in result.stdout.lower()
        assert "rest" not in result.stdout.lower()
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/test_integration_workflow.py -v`
Expected: PASS (validates all previous work)

**Step 3: Commit**

```bash
git add tests/test_integration_workflow.py
git commit -m "test: add integration tests for complete workflow"
```

---

### Task 11: README and Documentation

**Files:**
- Create: `README.md`
- Create: `docs/USAGE.md`
- Create: `docs/ARCHITECTURE.md`

**Step 1: Write project README**

```markdown
# README.md
# Tasty Dev - Feedback-Driven Development System

A Claude Code plugin that captures development insights through reflexion loops, accumulates expertise in ADRs and mulch, and improves planning decisions over time.

## Features

- **Reflexion Loop**: Automatically detects and captures development insights
- **ADR Management**: Strategic decisions with rationale
- **Mulch Integration**: Tactical patterns and how-to knowledge
- **Weekly Reviews**: Structured process for validating and synthesizing knowledge
- **Superpowers Integration**: Enhanced brainstorming and planning with accumulated expertise
- **Cross-Project Learning**: Knowledge repo for sharing insights across projects

## Installation

```bash
# Clone the plugin
git clone https://github.com/your-org/tasty-dev.git ~/.claude/plugins/tasty-dev

# Or install from marketplace
claude plugin install tasty-dev
```

## Quick Start

### 1. Initialize Your Project

```bash
cd your-project
bin/init-project-storage .
```

### 2. Use Enhanced Workflows

The plugin automatically enhances your development workflow:

- **Brainstorming**: Queries ADRs for strategic context
- **Planning**: Integrates ADR and mulch patterns
- **Implementation**: On-demand mulch queries
- **Reviews**: Captures insights automatically

### 3. Commands

- `/reflect` - Manually capture an insight
- `/correct` - Correct a previous decision
- `/review-project` - Run weekly project review
- `/review-knowledge` - Run knowledge repo review

## Workflow

```
Development work
    ↓
Reflexion trigger detected
    ↓
Insight captured to queue
    ↓
Weekly review processes queue
    ↓
Strategic → ADR | Tactical → Mulch
    ↓
Expertise informs future work
```

## Documentation

- [Usage Guide](docs/USAGE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Design Document](docs/plans/2026-03-07-feedback-driven-development-system-design.md)

## Development

```bash
# Run tests
pytest

# Run specific test
pytest tests/test_reflexion_triggers.py -v

# Integration tests
pytest tests/test_integration_workflow.py -v
```

## Requirements

- Python 3.8+
- Claude Code
- Mulch CLI (optional, for tactical knowledge)

## License

MIT
```

**Step 2: Write usage guide**

```markdown
# docs/USAGE.md
# Tasty Dev Usage Guide

## Setup

### First Time Setup

1. **Install the plugin**

```bash
claude plugin install tasty-dev
```

2. **Initialize your project**

```bash
cd your-project
bin/init-project-storage .
```

This creates `.tasty-dev/` directory with:
- `adr/` - Architecture Decision Records
- `mulch/` - Tactical knowledge
- `queue/` - Reflexion queue
- `config.yaml` - Configuration

3. **Configure knowledge repo (optional)**

Edit `.tasty-dev/config.yaml`:

```yaml
knowledge_repo: /path/to/shared/knowledge-repo
```

## Daily Usage

### Automatic Reflexion Capture

The system automatically detects reflexion triggers:

**Triggers:**
- Human deliberation (discussing options)
- Test failures
- Design conflicts
- Repeated friction

When triggered, Claude will:
1. Capture the insight
2. Classify as strategic or tactical
3. Add to queue for weekly review

### Manual Capture

Explicitly capture an insight:

```
/reflect
```

Claude will guide you through capturing:
- Context
- Initial suggestion
- Alternatives
- Resolution
- Why

### Querying Knowledge

**During design:**

Claude automatically queries ADRs when brainstorming:

```
User: Let's design the user authentication
Claude: [Queries ADRs for "authentication", "users"]
        Found ADR-0008: Use JWT for stateless auth
        [Designs within that constraint]
```

**During implementation:**

Claude queries mulch for tactical patterns:

```
User: Add integration tests for the API
Claude: [Queries mulch for "testing", "API"]
        Using pattern from mulch: testing/api-integration-tests
        [Generates tests following project pattern]
```

## Weekly Reviews

### Project Review

**Run weekly:**

```
/review-project
```

**Process:**

1. Review reflexion queue
2. Classify as strategic or tactical
3. Create ADRs for strategic items
4. Add mulch records for tactical items
5. Finalize draft ADRs
6. Sync to knowledge repo

**Time:** 15-30 minutes

### Knowledge Repo Review

**Run when universal knowledge needs synthesis:**

```
/review-knowledge
```

**Process:**

1. Detect patterns across projects
2. Promote recurrent patterns to universal
3. Resolve conflicts between projects
4. Maintain universal knowledge

**Time:** 30-60 minutes

## ADR Management

### Creating ADRs

**From reflexion:**

During project review, strategic reflexions become ADRs.

**Manual creation:**

```bash
bin/create-adr . "Use Event Sourcing for Audit Trail"
```

**Fill in template:**

- Context: Why is this decision needed?
- Decision: What are we doing?
- Alternatives: What else did we consider?
- Consequences: What are the trade-offs?

### Querying ADRs

```bash
bin/query-adr . "database"
bin/query-adr . "API design"
```

Returns relevant ADRs ranked by relevance.

### ADR Status

- **Draft**: Being written/validated
- **Accepted**: Finalized and in effect
- **Deprecated**: No longer applies
- **Superseded**: Replaced by another ADR

## Mulch Integration

### Adding Patterns

**From reflexion:**

During project review, tactical reflexions become mulch records.

**Manual addition:**

```bash
cd .tasty-dev/mulch
ml add testing "API integration test pattern" \
  --context "Use fixtures from tests/fixtures.py" \
  --why "Consistent setup across all API tests"
```

### Querying Mulch

```bash
bin/query-mulch . "testing"
bin/query-mulch . "database configuration"
```

### Mulch Domains

Organize by domain:
- `testing` - Test patterns
- `config` - Configuration patterns
- `patterns` - Code patterns
- `debugging` - Known issues and fixes
- `deployment` - Deployment procedures

## Best Practices

### 1. Respond to Reflexion Triggers

When Claude detects a trigger:
- Provide context about alternatives considered
- Explain why you prefer a certain approach
- Note if it applies broadly or just to this project

### 2. Weekly Reviews Are Important

Don't skip weekly reviews:
- Validates agent's classifications
- Captures expertise while fresh
- Prevents accumulated technical debt

### 3. ADRs for Strategy, Mulch for Tactics

**ADR:** Architecture, major technology choices, design patterns
**Mulch:** Implementation details, configurations, procedures

### 4. Reference ADRs in Code

```python
# See ADR-0012 for authentication approach
def authenticate_user(token: str) -> User:
    # Implementation following ADR-0012
```

### 5. Keep Mulch Actionable

Good mulch:
- "Use connection pooling with max 20 connections"
- "Run migrations with --no-backup flag in CI"

Bad mulch:
- "Database stuff"
- "Be careful with queries"

## Troubleshooting

### Hook Not Triggering

Check plugin is installed:

```bash
claude plugin list
```

Reinstall if needed:

```bash
claude plugin install tasty-dev --force
```

### ADR Query Returns Nothing

Verify ADRs exist:

```bash
ls .tasty-dev/adr/
```

Check ADR content has relevant keywords.

### Mulch CLI Not Found

Install mulch CLI:

```bash
# Installation instructions at mulch repo
```

Or use plugin without mulch (ADRs only).
```

**Step 3: Write architecture document**

```markdown
# docs/ARCHITECTURE.md
# Tasty Dev Architecture

## Overview

Tasty Dev is a feedback-driven development system built as a Claude Code plugin. It captures development insights through reflexion loops and accumulates expertise over time.

## Components

### 1. Plugin System

**File:** `plugin.yaml`

Defines:
- Commands (`/reflect`, `/review-project`, etc.)
- Hooks (trigger detection, weekly nudges)
- Skills (enhanced workflows)

### 2. Project Storage

**Location:** `.tasty-dev/` in each project

**Structure:**
```
.tasty-dev/
├── adr/           # Architecture Decision Records
├── mulch/         # Tactical knowledge (if mulch installed)
├── queue/         # Pending reflexions
└── config.yaml    # Project configuration
```

### 3. Knowledge Repo (Optional)

**Location:** Shared directory across projects

**Structure:**
```
knowledge-repo/
├── projects/
│   ├── project-a/
│   │   ├── mulch/
│   │   └── adr/
│   └── project-b/
└── universal/     # Promoted cross-project knowledge
    ├── mulch/
    └── adr/
```

## Data Flow

### Reflexion Loop

```
1. Trigger Detection (hooks/detect_reflexion_triggers.py)
   ↓
2. Capture (bin/capture-reflexion)
   ↓
3. Queue Storage (.tasty-dev/queue/*.json)
   ↓
4. Weekly Review (bin/run-project-review)
   ↓
5. Classification & Routing
   ├→ Strategic → ADR (bin/create-adr)
   └→ Tactical → Mulch (ml add)
```

### Knowledge Query

```
Design/Implementation Phase
   ↓
Query ADRs (bin/query-adr)
Query Mulch (bin/query-mulch)
   ↓
Load Relevant Knowledge
   ↓
Inform Decisions
```

## Skills Integration

### Enhanced Superpowers

Standard superpowers skills are enhanced:

| Standard Skill | Enhancement | Files |
|----------------|-------------|-------|
| brainstorming | Queries ADRs first | skills/superpowers-enhanced/brainstorming-enhanced.md |
| writing-plans | Integrates ADR + mulch | skills/superpowers-enhanced/writing-plans-enhanced.md |
| executing-plans | On-demand mulch queries | (Phase 4, not in this plan) |
| systematic-debugging | Known issues lookup | (Phase 4, not in this plan) |

### Workflow

```
User request
   ↓
Standard skill triggered
   ↓
Enhanced version activated
   ↓
Queries knowledge (ADR/mulch)
   ↓
Informed execution
   ↓
Captures new insights
```

## Hooks

### 1. Reflexion Trigger Detector

**File:** `hooks/detect_reflexion_triggers.py`

**Events:** `tool_result`, `user_message`

**Logic:**
- Pattern matching on user messages
- Test failure detection
- Design conflict detection

**Output:** Triggers reflexion capture

### 2. Weekly Review Nudge

**File:** `hooks/nudge_weekly_review.py`

**Events:** `session_start`, `task_complete`

**Logic:**
- Check last review date
- Day 7: Gentle reminder
- Day 10+: Prominent reminder

**Output:** Nudge message to user

## Tools

### Command-Line Tools

All tools in `bin/`:

| Tool | Purpose | Usage |
|------|---------|-------|
| init-project-storage | Initialize .tasty-dev/ | `bin/init-project-storage <path>` |
| capture-reflexion | Capture insight to queue | `echo '{...}' \| bin/capture-reflexion <path>` |
| create-adr | Create new ADR | `bin/create-adr <path> "<title>"` |
| query-adr | Search ADRs | `bin/query-adr <path> "<query>"` |
| query-mulch | Search mulch | `bin/query-mulch <path> "<query>"` |
| run-project-review | Run weekly review | `bin/run-project-review <path>` |

### Integration with Mulch CLI

Mulch CLI (`ml`) is used for tactical knowledge:

```bash
ml add <domain> "<description>"  # Add record
ml search <query>                # Search records
ml edit <id>                     # Edit record
ml delete <id>                   # Delete record
ml doctor --fix                  # Resolve conflicts
```

Tasty Dev wraps mulch for integration:
- `bin/query-mulch` wraps `ml search`
- Weekly review uses `ml add` for tactical items

## Configuration

### Project Config

**File:** `.tasty-dev/config.yaml`

```yaml
knowledge_repo: /path/to/shared/repo  # Optional
last_project_review: "2026-03-07T10:00:00"
last_knowledge_review: null
```

### Plugin Config

**File:** `plugin.yaml` (in plugin directory)

Defines plugin metadata and entry points.

## Extension Points

### Adding New Skills

1. Create skill in `skills/`
2. Add to `plugin.yaml` commands section
3. Implement skill logic
4. Add tests

### Adding New Hooks

1. Create hook in `hooks/`
2. Add to `plugin.yaml` hooks section
3. Implement hook logic
4. Add tests

### Customizing Classification

Edit `bin/capture-reflexion`:

```python
def infer_classification(reflexion: dict) -> dict:
    # Add custom logic
    # Strategic vs tactical
    # Project-specific vs universal
```

## Security Considerations

### Sensitive Data

- ADRs and mulch may contain sensitive information
- Store `.tasty-dev/` in private repos only
- Add to `.gitignore` if needed

### Knowledge Repo

- If using shared knowledge repo, ensure access controls
- Review promoted universal knowledge before syncing
- Don't sync project-specific secrets

## Performance

### Hook Performance

Hooks run on every relevant event:
- Keep trigger detection fast (<100ms)
- Use simple pattern matching
- Avoid expensive operations

### Storage

- Reflexion queue cleaned up after review
- ADRs are markdown (small)
- Mulch uses efficient storage

## Future Enhancements

Planned for Phase 4+:

1. **Knowledge Repo Sync** - Automatic push/pull
2. **Cross-Project Promotion** - Automated promotion suggestions
3. **More Superpowers Integration** - debugging, verification, etc.
4. **Applicability Filtering** - Tech stack awareness
5. **Conflict Detection** - Automatic ADR violation detection
```

**Step 4: Commit all documentation**

```bash
git add README.md docs/USAGE.md docs/ARCHITECTURE.md
git commit -m "docs: add comprehensive documentation"
```

---

## Completion

**Plan complete and saved to `docs/plans/2026-03-07-feedback-driven-development-implementation.md`.**

**Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach would you like?**
