# ADR Author Skill Adaptation Design

**Date:** 2026-03-27

## Summary

Adapt the ADR author skill from a domain-specific, hardcoded tool (originally built for a Databricks data pipeline project) into a project-agnostic skill conforming to tasty-dev's architecture. The skill becomes the sole way to create and review ADRs across any project using tasty-dev.

## Decisions Made During Design

- **ADR format:** Upgrade to MADR with YAML frontmatter (status, date, decision-makers, domains, affects, discussion metadata)
- **Storage scope:** Project-local in `.tasty-dev/adr/`, cross-project awareness deferred to Phase 4
- **Bootstrap:** Via `init-project-storage` when `.tasty-dev/` is missing
- **Examples:** Context-aware — generic when no ADRs exist, learned from existing ADRs thereafter. Important for future ADR classification when promoting to centralized repo since domain-specific ADRs need rework before they're universally useful.
- **Feature set:** Keep full creation workflow (Steps 1-9) and full review/discussion system (review queues, chronological navigation, comment threading, approval, Claude as AI facilitator)
- **Enforcement:** Drop from this skill. Becomes a separate cross-cutting tasty-dev concern in Phase 2.5 covering ADRs, mulch, and reflexions holistically.
- **ADR lifecycle ownership:** Skill owns it entirely. Remove `bin/create-adr` and `bin/query-adr`. No "fast path" — the conversation IS the value.
- **Template forward-compatibility:** `enforces` field stays in MADR template as empty placeholder, populated when enforcement is built.
- **Path resolution:** Find `.tasty-dev/config.yaml` by walking up from cwd or via git root. Its existence confirms project root. No absolute paths stored in config (different people check out projects in different locations). Config stays as-is: `knowledge_repo`, `last_project_review`, `last_knowledge_review`.
- **Git operations:** Manual commit mode per user preferences. Skill never commits or pushes.

## File Changes

### Modify

- `skills/adr/skill.md` — Strip domain content, parameterize paths, remove guardian/enforces workflow, make examples context-aware, keep full creation and review/discussion systems
- `templates/adr-template.md` — Upgrade to MADR format with YAML frontmatter and discussion section
- `SKILL.md` — Register `adr-author` command with creation and review modes
- `skills/adr/TESTING.md` — Rewrite for development-time validation with seed data

### Remove

- `bin/create-adr` — Skill owns creation
- `bin/query-adr` — Query functionality absorbed into skill's review mode and context loading
- `tests/test_adr_query.py` — No longer relevant

### Rewrite

- `tests/test_adr_creation.py` — Test `init-project-storage` creates `.tasty-dev/adr/` and MADR template has valid YAML frontmatter

## MADR Template

```yaml
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

## SKILL.md Registration

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

## Skill Adaptation Details

### Path Resolution

1. Walk up from cwd or use `git rev-parse --show-toplevel` to find `.tasty-dev/config.yaml`
2. If found: that directory's parent is the project root
3. If not found: offer to bootstrap via `init-project-storage`
4. All subsequent operations use `PROJECT_ROOT/.tasty-dev/adr/`

### Context-Aware Examples

Tiered approach replacing hardcoded domain examples:

- **No existing ADRs:** Use 2-3 generic software engineering examples (database choice, API versioning, monolith vs services)
- **Existing ADRs present:** Read during Step 1 (Initialize Context) and derive examples, patterns, and suggestions. Feeds option suggestions (Steps 4b-4d) and skeptical review (Step 5, referencing past decisions)

### Content Stripped

- All Databricks/Unity Catalog/DLT/medallion architecture references
- All hardcoded paths to `core_data_pipeline`
- Guardian skill handoff logic (Steps 1, 4a "handoff context")
- Step 6c enforces rule generation workflow (field stays in template)

### Content Preserved and Adapted

- Steps 1-9 creation workflow
- Skeptical review (Step 5)
- All review modes (queue, specific ADR, chronological navigation)
- Comment threading with critical analysis
- Approval workflow
- Claude as AI facilitator
- Manual git commit mode
- User identity detection via git config

## Testing Strategy

Development-time only — test materials stay in this repo but don't ship with the plugin.

- Seed a test project with `.tasty-dev/` and 2-3 dummy ADRs to exercise review/discussion features
- Validate creation workflow on a real ADR in a real project
- `tests/test_adr_creation.py` rewritten for init + template validation

## Meta-Plan: Phases to Daily Production

### Phase 1: Adapt & Validate (this work)

- Refactor skill, upgrade template, update SKILL.md, remove CLI tools
- Seed test project with `.tasty-dev/` and 2-3 dummy ADRs
- Exercise review/discussion/approval features against seed data
- Validate creation workflow on a real ADR in a real project
- **Exit:** Skill works end-to-end, creation and review both functional

### Phase 1.5: Telemetry Infrastructure

- User-level init (`~/.tasty-dev/config.toml` with telemetry toggle)
- Trace writer utility (`bin/write-telemetry-trace`)
- Version and telemetry expectations added to all skill frontmatters
- Telemetry instructions appended to all skills
- Health assessment skill for analyzing collected traces
- **Exit:** End-to-end smoke test passes (init → enable → write trace → read trace)
- **Design doc:** `docs/plans/2026-03-28-skill-telemetry-design.md`

### Phase 2: Single Project Production

Validate the full tasty-dev system on an in-flight project. Not just adr-author — the entire feedback loop across all skills. The project will have existing history and decisions, so the loop won't follow a prescribed order.

**Two feedback cycles required.** A cycle is complete when an insight captured by the system has influenced a later decision or piece of work.

**Capabilities exercised (Cycle 1, solo):**

- [ ] Reflexion captured (at least 1 strategic, 1 tactical)
- [ ] ADR created via `/adr-author` (from any trigger — fresh decision, retroactive documentation, or queued reflexion)
- [ ] Mulch entry created from tactical insight
- [ ] Weekly review run and processes at least 1 queued item
- [ ] Brainstorming or planning session that references existing ADR or mulch
- [ ] Telemetry traces exist for each skill invoked

**Capabilities exercised (Cycle 2, with teammate):**

- [ ] Teammate reviews and comments on an ADR
- [ ] ADR approved through approval workflow
- [ ] Teammate generates at least 1 reflexion trace
- [ ] Telemetry traces show both users

**System-level validation:**

- [ ] Health assessment produces a meaningful report
- [ ] Every skill in the suite has at least 1 invocation trace
- [ ] At least 1 insight from the system demonstrably influenced later work (the loop closed)

**Iterate on:** generic examples quality, skeptical review without domain context, review queue accuracy, context-aware suggestions as ADRs accumulate, reflexion trigger sensitivity, mulch accumulation rate

### Phase 2.5: Enforcement Foundation

- Build as a cross-cutting tasty-dev concern, not ADR-specific
- New skill: conversational compliance check ("how are we tasting?")
- Checks codebase against ADR `enforces` rules, mulch patterns, reflexion insights
- ADR author skill begins populating `enforces` field during creation (Step 6c reactivated)
- Future path: pre-commit hook that validates compliance and captures newly made decisions
- **Exit:** Can run a compliance check and get meaningful, actionable results

### Phase 3: Multi-Project Production

- Bring tasty-dev to a second project via `init-project-storage`
- Validate clean bootstrap with zero existing ADRs
- Validate with different team and different domain
- Expect to feel the absence of cross-project awareness
- **Exit:** Running on 2-3 projects, with concrete examples of decisions that should have cross-pollinated

### Phase 4: Cross-Project Knowledge

- Build `knowledge_repo` sync via `config.yaml`
- ADR promotion: project-local to centralized, with domain-context transformation
- Skill reads centralized repo during context initialization for cross-project suggestions
- Weekly review pulls universal updates
- **Trigger to start:** Actively maintaining ADRs in 2+ projects with concrete missed cross-pollination examples

### Future: Enforcement as Automated Gate

- Pre-commit hook validates compliance
- Captures newly made decisions from committed code
- Enforcement covers ADRs, mulch, reflexions holistically
