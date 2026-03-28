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
