# Skill Telemetry Design

**Date:** 2026-03-28

## Summary

A two-part telemetry system for tasty-dev: invocation traces written by every skill after each run, and a health assessment skill that analyzes collected traces against declared expectations. Primary consumer is the skill author validating that the system works across projects, users, and teams. Future path: skills reading their own traces to self-improve.

## Decisions Made During Design

- **Primary consumer:** Skill author (you), for validation and refinement. Self-improvement by skills themselves is a future goal if this proves useful.
- **Trace granularity:** Step-level traces. Outcome-only is too sparse for diagnosis. Full conversation logs are a privacy concern and unnecessary.
- **Storage location:** User-local at `~/.tasty-dev/telemetry/`. Never enters git. One place to look across all projects.
- **Project identifier:** Git remote slug (e.g., `github.com-org-project-alpha`). Portable across machines.
- **Skill versioning:** Individual skills get `version` in frontmatter, plus tasty-dev system version. Both recorded in traces.
- **Expectations:** Each skill declares expected cadence, participation model, and health signals in its frontmatter. Health assessment reads these — no hardcoded assumptions in the assessment skill.
- **Health signals format:** Natural language interpreted by Claude, not rigid schema. Flexible as skills evolve.
- **Toggle:** User-level `~/.tasty-dev/config.toml` with `telemetry.enabled = false` by default. File created during user-level init. Opt-in, not opt-out.
- **Config format:** TOML, not YAML. TOML is unambiguous and stdlib in Python 3.11+.
- **Collection from others:** Users zip `~/.tasty-dev/telemetry/` and send it. No network transmission, no automation needed yet.
- **Health assessment location:** Development-time skill in this repo, not deployed with the plugin.
- **Absence detection:** No special mechanism needed. Health assessment reads traces that exist and evaluates against expectations — absence of traces IS the signal.
- **Scope:** All skills in tasty-dev suite, not just adr-author.
- **Timing:** Build before Phase 2 so every real-project invocation generates traces from the start.

## Invocation Trace Format

### File Location

```
~/.tasty-dev/telemetry/{git-remote-slug}/{timestamp}-{skill-name}.md
```

Example: `~/.tasty-dev/telemetry/github.com-org-project-alpha/2026-03-28T07-45-adr-author.md`

### File Structure

```markdown
---
skill: adr-author
skill_version: 0.1.0
tastydev_version: 0.1.0
mode: review
project: git@github.com:org/project-alpha.git
user: zac
timestamp: 2026-03-28T07:45:00
---

## Steps

- [completed] Resolve project root — found .tasty-dev/config.yaml
- [completed] Detect user identity — zac (from git config)
- [completed] Build review queue — 1 ADR queued, 1 skipped (draft)
- [completed] Comment workflow — reply to Alice's thread
  - Critical analysis: strength=pass, contribution=marginal, consistency=pass
  - User action: posted as-is
- [completed] Approval workflow — approved with comment
  - Status changed: proposed → accepted

## Outcome

- ADRs reviewed: 1
- Comments added: 2
- Status changes: 1

## Issues

None
```

### Design Choices

- Markdown, not JSON — human-readable, easy to review before sending
- YAML frontmatter — machine-parseable for health assessment (note: YAML in frontmatter only, not as standalone config)
- Step entries follow `[status] verb — detail` convention
- No user content captured (no comment text, no ADR content, no decision details)
- Abandoned workflows record which step and why

## Skill Expectations Declaration

Each skill declares expected usage in its frontmatter:

```toml
# Example: adr-author
version: 0.1.0
telemetry:
  expected_cadence: on_demand
  expected_participants: all
  health_signals:
    - "at least 1 invocation per project per month"
    - "review mode should run within 7 days of a new proposed ADR"
```

```toml
# Example: project-weekly-review
version: 0.1.0
telemetry:
  expected_cadence: weekly
  expected_participants: at_least_one
  health_signals:
    - "should run every 7-10 days per project"
    - "gap > 14 days is unhealthy"
```

```toml
# Example: reflexion-capture
version: 0.1.0
telemetry:
  expected_cadence: organic
  expected_participants: all
  health_signals:
    - "each active team member should have traces"
    - "0 reflexions in 14 days of active development is a red flag"
```

### Fields

- `version` — skill version, new field for all skills
- `expected_cadence` — `weekly`, `on_demand`, `organic`
- `expected_participants` — `all` (everyone), `at_least_one` (team-level)
- `health_signals` — natural language expectations evaluated by health assessment skill

## Toggle Mechanism

**File:** `~/.tasty-dev/config.toml`

```toml
[telemetry]
enabled = false
```

- Created during user-level init with telemetry disabled by default
- Skills check before writing traces; skip silently if disabled or file missing
- User explicitly enables when willing to help improve the system

## Health Assessment Skill

**Location:** `skills/health-assessment/skill.md` (development-time, not deployed)

**Invocation:** `/health-assessment` or `/health-assessment --project github.com-org-project-alpha`

**Process:**
1. Read trace files from provided path (`~/.tasty-dev/telemetry/` or unzipped folder)
2. Read each skill's frontmatter for `telemetry.health_signals`
3. Evaluate signals against traces
4. Produce health report

**Example output:**

```
## System Health: github.com-org-project-alpha
Period: 2026-03-15 to 2026-03-28 (13 days)

### Healthy
- adr-author: 5 invocations, 3 users, 2 ADRs created, 3 reviewed
- reflexion-capture: 8 invocations across 3 users

### Warnings
- project-weekly-review: last ran 11 days ago (expected: every 7-10 days)
- reflexion-capture: bob has 0 traces (alice: 5, zac: 3)

### Issues
- adr-author: skeptical review skipped in 2/5 invocations
- No mulch activity in 13 days
```

## Changes to Existing Skills

Every skill in the suite needs:

1. **Frontmatter additions** — `version` and `telemetry` block with expectations
2. **End-of-workflow telemetry step** — Standard instruction block:

```markdown
## Telemetry

After completing this workflow (whether successful, abandoned, or errored):

1. Check if `~/.tasty-dev/config.toml` exists and `telemetry.enabled = true`
2. If enabled, write an invocation trace to `~/.tasty-dev/telemetry/{git-remote-slug}/{timestamp}-{skill-name}.md`
3. Include: frontmatter (skill, version, mode, project, user, timestamp), step-level trace, outcome summary, and any issues encountered
4. If the workflow was abandoned mid-step, record which step and why
```

**Skills to update:**
- `adr/skill.md`
- `reflexion/capture.md`
- `reviews/project-weekly.md`
- Any future skills

**Also needed:**
- User-level init mechanism that creates `~/.tasty-dev/config.toml`
- `version` field added to `SKILL.md` system manifest

## Implementation Timing

Build telemetry before Phase 2 of the meta-plan so that every real-project invocation generates traces from the start. At Phase 2 exit, run health assessment to validate exit criteria with data rather than feel.

## Challenging Scenarios This Enables

- **ADR merge conflicts** — traces show two concurrent adr-author create invocations; health assessment flags potential renumbering issues
- **Weekly review not running** — absence of project-weekly-review traces beyond expected cadence
- **Uneven team participation** — per-user trace counts reveal who isn't generating reflexions
- **Mulch rate** — trace frequency for mulch-related skills shows whether tactical knowledge is accumulating
- **Skeptical review skipping** — step-level traces show [skipped] entries in adr-author
- **Expert agent utilization** — traces show which skills/modes are actually used vs available
