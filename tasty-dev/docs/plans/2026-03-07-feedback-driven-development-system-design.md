# Feedback-Driven Development System Design

**Date:** 2026-03-07
**Status:** Draft
**Author:** System Design via Brainstorming

## Overview

A coordinated system of skills and processes that captures development insights, accumulates expertise, and improves planning and implementation decisions over time through structured feedback loops.

## Purpose

Enable human-agent collaboration that:
- Captures insights that are difficult to articulate in the moment
- Refines understanding through actual usage
- Makes better decisions over time without re-explaining everything
- Compounds learning across all projects, not just one

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│  PLUGIN (portable, versioned)                               │
│  ─────────────────────────────────────────────────────────  │
│  - Skills: reflexion, planning enhancement, review          │
│  - Commands: /review-project, /review-knowledge             │
│  - Hooks: trigger detection, enforcement                    │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│  PROJECT STORAGE (per-project)                              │
│  ─────────────────────────────────────────────────────────  │
│  - ADRs: Strategic decisions with rationale                 │
│  - Mulch: Tactical patterns and expertise                   │
│  - Queue: Deferred reflections                              │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│  KNOWLEDGE REPO (cross-project synthesis)                   │
│  ─────────────────────────────────────────────────────────  │
│  projects/                                                  │
│  ├── project-a/                                             │
│  │   ├── mulch/                                             │
│  │   └── adr/                                               │
│  ├── project-b/                                             │
│  └── project-c/                                             │
│                                                             │
│  universal/           ← promoted knowledge                  │
│  ├── mulch/                                                 │
│  └── adr/                                                   │
└─────────────────────────────────────────────────────────────┘
```

### Knowledge Layers

| Layer | Purpose | Examples |
|-------|---------|----------|
| **ADRs** | Strategic decisions and rationale | "Use PostgreSQL because...", "Event sourcing for audit trail" |
| **Mulch** | Tactical patterns and how-to | "Connection pooling config", "Test fixture patterns" |
| **Relationship** | Complementary | ADRs set boundaries, mulch fills in details. They reference each other. |

### Phase-Aware Knowledge Consumption

```
┌─────────────────────────────────────────────────────────────┐
│  DESIGN PHASE (brainstorming, /write-plan)                  │
│  ─────────────────────────────────────────                  │
│  Queries: ADRs (on-demand as topics arise)                  │
│  Focus: Architecture, boundaries, major decisions           │
│  Output: Design doc + implementation breadcrumbs            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  IMPLEMENTATION PHASE (/execute-plan, task work)            │
│  ─────────────────────────────────────────                  │
│  Queries: Mulch (on-demand during execution)                │
│  Focus: How to build it, patterns, edge cases               │
│  Informs: Every aspect of implementation plan               │
└─────────────────────────────────────────────────────────────┘
```

## Reflexion Loop

The core feedback mechanism that captures insights and routes them appropriately.

### Step 1: Trigger Detection

| Trigger Category | Examples |
|------------------|----------|
| **Human deliberation** | Any discussion, weighing options, clarification, modification, "think differently" |
| **System failure** | Tests fail, build breaks, linter errors |
| **Design conflict** | Implementation discovers ADR assumption wrong |
| **Repeated friction** | Same question multiple times, same area modified repeatedly |
| **User invocation** | Explicit `/reflect` or `/correct` command |

**Key insight:** Any human interaction that isn't full acceptance is a trigger. Discussions and deliberation are valuable signals.

### Step 2: Capture

Record:
- **Context** - What task/goal were we working on?
- **Initial suggestion** - What did the agent propose?
- **Alternatives considered** - What other options were discussed?
- **Friction point** - What was the concern, failure, or discussion?
- **Resolution** - What was decided? What happened?
- **Why** - Rationale for resolution and why alternatives were rejected

### Step 3: Classify

Agent infers classification (validated during weekly review):

**Level:**
- Strategic (ADR-level) - Affects architecture, major boundaries
- Tactical (mulch-level) - Patterns, conventions, how-to knowledge

**Scope:**
- Project-specific - Only applies to this codebase
- Potentially universal - Might apply across projects (promotion candidate)

### Step 4: Route

| Classification | Immediate Action | Weekly Review Action |
|----------------|------------------|---------------------|
| Strategic + Major | Draft ADR immediately | Finalize ADR |
| Strategic + Minor | Queue for review | Draft and finalize ADR |
| Tactical + Any | Record to mulch, tag if promotion candidate | Validate classification |

### Step 5: Propagate

When ADR is created or updated:

1. **Prompt user:** "Flag dependent artifacts for later, or update them now?"
2. **Default behavior:** Flag artifacts, notify when touched
3. **Optional:** Eager update of dependent artifacts

Cascade: ADR changed → Design plans flagged → Implementation plans flagged → Active tasks flagged

## Conflict Handling

**Severity-based response:**

| Severity | Trigger | Response |
|----------|---------|----------|
| **Major** | Implementation challenges ADR assumption, blocks progress | Pause immediately, escalate to user, may cascade to design/plan updates |
| **Minor** | Tension between suggestion and context, doesn't block work | Flag and continue, queue for weekly review |

**Maturity effect:**
- Early project: Many major conflicts, frequent pauses, rapid ADR/mulch accumulation
- Mature project: Mostly minor tensions, weekly review handles most
- **Cross-project maturity:** As system improves across many projects, all new projects start smarter

## Weekly Reviews

### Project Weekly Review

**Cadence:** Weekly per project (different schedules per project)

**Process:**

1. **Process queue** - Handle deferred reflections and decisions
2. **Project trend analysis** - Review git history, conversation patterns, repeated friction
3. **Validate classifications** - Review agent's strategic/tactical classifications
4. **Finalize ADRs** - Complete any queued strategic insights
5. **Sync to knowledge repo** - Push project's mulch + ADRs
6. **Pull universal updates** - Get promoted knowledge from other projects
7. **Plan review** - Review plans with attention to new/changed universal knowledge, resolve conflicts

**Enforcement:** Escalating nudge
- Day 7: Gentle reminder
- Day 10+: More prominent (session start, after task completion)
- Never blocks work, but doesn't let reflection slip indefinitely

### Knowledge Repo Weekly Review

**Cadence:** Weekly (triggered by any project noticing stale universal updates)

**Process:**

1. **Recurrence detection** - Scan for patterns appearing across `projects/*/`
2. **Promotion decisions** - Review candidates with cross-project evidence
3. **Conflict resolution** - Handle contradictions between projects
4. **Cross-project trend analysis** - Patterns across entire development practice
5. **Universal knowledge maintenance** - Refine, update, deprecate promoted insights
6. **Synthesis changelog** - Document what was promoted, deprecated, trends identified

**Promotion Signals:**

| Signal | Weight | Description |
|--------|--------|-------------|
| **Recurrence across projects** | Strongest | Same pattern in multiple codebases |
| **Recurrence within shared expertise area** | Strong | Same mulch domain across projects |
| **Measured value** | High | Demonstrated impact on goals (performance, reliability, velocity) |
| **Domain-agnostic** | Medium | Doesn't depend on specific stack |
| **Fundamental** | Medium | About development practice itself |
| **Stability** | Medium | Hasn't been contradicted (but can be disrupted by demonstrated value) |
| **Explainability** | Medium | The "why" transfers outside original context |

**Promotion mechanism:** Concise proposal with evidence during weekly review, user approves/rejects/defers.

**Trigger for repo review:** Any project doing weekly review that pulls universal updates and finds nothing new since last pull.

## Mulch Conflict Resolution

Uses mulch's native mechanisms:
- `--supersedes` flag to mark records that replace prior knowledge
- `--relates-to` flag for cross-domain references
- Classification tiers (foundational > tactical > observational)
- `ml doctor --fix` for deduplication
- `ml edit` / `ml delete` for manual resolution

**Process:** Conflicts detected during weekly review, resolved using these tools. Universal mulch typically classified as foundational tier. Project-specific mulch can supersede with justification.

## Superpowers Integration

Enhanced workflow for existing superpowers skills:

| Skill | Enhancement |
|-------|-------------|
| **brainstorming** | Queries ADRs for strategic context, proposals align with decisions, surfaces conflicts explicitly |
| **writing-plans** | Queries ADRs + mulch extensively (not just breadcrumbs), every aspect informed by accumulated expertise |
| **executing-plans** | On-demand mulch queries during task execution, unknown areas flagged and resolved |
| **systematic-debugging** | Known issues are instant lookups in mulch, new issues become future instant lookups |
| **verification-before-completion** | Project-aware checklist from mulch (not generic) |
| **requesting-code-review** | PR descriptions reference ADRs, highlight new mulch patterns, note queued reflections |
| **receiving-code-review** | Reviewer feedback triggers reflexion, expertise flows into mulch |
| **finishing-a-development-branch** | Checks for draft ADRs to finalize, queued items to defer |

**Full workflow example:** See "Adding API Endpoint" scenario in brainstorming session.

## System Evolution

```
Phase 1: Early Projects
┌────────────────────────────────────────┐
│  Many major conflicts                  │
│  → Frequent pauses for human input     │
│  → ADRs being established/refined      │
│  → Mulch accumulating rapidly          │
│  → Plans frequently revised            │
└────────────────────────────────────────┘

Phase 2: Mature Single Project
┌────────────────────────────────────────┐
│  Mostly minor tensions                 │
│  → Weekly review handles most issues   │
│  → ADRs stable, occasional additions   │
│  → Mulch refinement, less churn        │
│  → Plans hold up well                  │
└────────────────────────────────────────┘

Phase 3: Cross-Project Maturity
┌────────────────────────────────────────┐
│  New projects start smart              │
│  → Inherit universal expertise         │
│  → Fewer conflicts from the beginning  │
│  → Faster ramp-up, better defaults     │
│  → Continuous improvement across all   │
└────────────────────────────────────────┘
```

**Key principle:** Learning compounds across the entire development practice, not just within one codebase.

## Knowledge Distillation Pipeline

```
Project work generates insights
         ↓
Reflexion loop captures and routes
         ↓
Project weekly review validates and syncs
         ↓
Knowledge repo accumulates all projects
         ↓
Repo weekly review detects recurrence
         ↓
Promotion decisions based on evidence
         ↓
Universal expertise grows
         ↓
All projects pull and benefit
```

## Open Questions

1. **Applicability filtering** - How to prevent Python patterns from surfacing in Go projects? Start simple (basic tech detection), refine if problematic.

2. **Skills inventory** - What specific commands/hooks need to be built?
   - `/review-project` command
   - `/review-knowledge` command
   - `/reflect` and `/correct` commands
   - Hook to detect reflexion triggers
   - Hook to enforce weekly review nudges
   - Skills to enhance superpowers integration

3. **Plugin structure** - How to package this system?
   - Manifest defining commands and hooks
   - Skills for each enhancement
   - Integration points with existing superpowers
   - Configuration for knowledge repo location

4. **ADR skill specifics** - Creation, enforcement, templates
   - Need skill for creating ADRs
   - Need skill for querying ADRs during design
   - Need enforcement that checks for ADR violations
   - Standard ADR template (problem, decision, alternatives, consequences)

## Success Criteria

- **Reduced repeated mistakes** - Same error doesn't happen twice
- **Faster planning** - Brainstorms skip settled decisions, focus on new problems
- **Better implementation plans** - Plans reflect project-specific patterns automatically
- **Shorter debugging** - Known issues are instant lookups
- **Cross-project learning** - New projects benefit from all previous projects
- **Improved developer experience** - Less time explaining, more time building
- **Tasteful defaults** - System suggests project-appropriate solutions without prompting

## Next Steps

1. Review and validate this design
2. Create implementation plan for plugin structure
3. Identify integration points with existing superpowers
4. Build MVP focusing on core reflexion loop
5. Test with current project (core_data_pipeline)
6. Iterate based on real usage