# Tasty-dev Ecosystem — Product Requirements

**Date:** 2026-03-31

## Summary

Product requirements for the tasty-dev development ecosystem, organized by SDLC phase. These requirements define what knowledge should be available, when it should be loaded, and how learnings should be captured at each stage of the development lifecycle. The ecosystem includes ADRs (strategic decisions), mulch (tactical knowledge), reflexions (insight capture), and weekly reviews (maintenance heartbeat).

## Context

Tasty-dev is a development ecosystem that includes mulch (adopted from jayminwest/mulch) as its tactical knowledge layer and ADRs as its strategic decision layer. It sits alongside external development skill suites (e.g., obra/superpowers) and must cooperate with them without assuming control. When tasty-dev is enabled on a project, its skills should trigger at the correct times and augment the development process regardless of which other skill suites are present.

## Requirements by SDLC Phase

### Requirement 1: Brainstorming / Requirements Gathering

Before brainstorming or planning, a summary of ADRs with relevant domains should be available — not the full ADR content, but enough to know what decisions exist and where gaps are. Mulch is excluded at this stage — it is noise and distracting during high-level ideation.

The planning process should be able to query specific ADRs in depth when needed (e.g., via subagent). When planning identifies architectural gaps (decisions that should exist but don't), those gaps should be captured for follow-up by the ecosystem.

### Requirement 2: High-Level Design

When making architectural choices during high-level design, full ADR content should be accessible for the ADRs identified as relevant during the brainstorming/requirements phase. The set of relevant ADRs is scoped by the preceding phase, not loaded broadly.

When a proposed approach touches an area covered by an existing ADR, that ADR should be surfaced. When a proposed approach would modify, update, or reverse an existing ADR, that should be explicitly called out. When a proposed approach touches an area with no ADR, that gap should be noted.

The ecosystem should track ADR needs — not force immediate creation. Tracked ADR needs may result in:

- A spike/research task within the implementation plan
- An implementation blocker requiring resolution outside the typical process
- A deferred ADR to be created when most appropriate

The weekly review should follow up on unresolved ADR needs.

### Requirement 3: Implementation Planning

Mulch domains relevant to the implementation tasks should be loaded. For example, if a task involves writing tests, load the testing domain; if it involves API work, load the api domain. This is the first phase where mulch enters the workflow.

ADR summaries remain available as constraints (not full content — that was the high-level design phase's concern). The plan should reference which mulch patterns and ADR constraints informed each task.

If the plan calls for work in an area where no mulch exists, that is expected — it means there is no accumulated knowledge yet, not a gap to flag.

### Requirement 4: Implementation / Coding

Mulch domains relevant to the specific task being worked on should be loaded — not all mulch, just what applies to the current task's domain.

ADRs are not proactively loaded during implementation. Compliance checking happens at pre-commit time, not during active coding.

During implementation, any signal is an opportunity to extract tactical learnings for mulch:

- Failed tests
- Developer questions
- Unexpected behavior
- Successful execution of a plan

These captures should happen organically during development, not only when the developer explicitly notices something. Strategic learnings (potential ADR needs) are captured during the pre-commit phase when the work is largely functional and tested.

### Requirement 5: Testing

Mulch testing domain and task-relevant testing subdomains should be loaded when writing or debugging tests.

Test failures are a prime signal for tactical learning capture. Test patterns that emerge — fixture setup, mocking conventions, integration test structure — should be captured as mulch when they solidify.

No special ADR behavior during testing. Compliance checking happens at pre-commit.

### Requirement 6: Pre-Commit

Before committing, check completed work against existing ADRs for compliance. This is the enforcement checkpoint applied at a natural moment in the workflow.

When contradictions are found, the appropriate responses are:

- Adjust the code to match existing ADRs
- Amend an ADR that is not yet fully accepted (still in progress)
- Create now or defer creation of a new ADR that documents the decision, effectively overriding any earlier contradicting ADR

Capture any strategic learnings that emerged during implementation as ADR needs. Perform a final sweep for tactical learnings that were not captured during implementation.

### Requirement 7: Code Review

Both ADRs and mulch are in the repo and naturally available to reviewers. No special ecosystem behavior is required to load knowledge during review.

When a developer fixes issues surfaced by PR commentary, those new commits are the surface where tactical learnings (mulch) and architectural decisions (ADR needs) get captured — through the same implementation and pre-commit mechanisms described in Requirements 4 and 6.

### Requirement 8: Build / Deploy

No distinct ecosystem behavior. Build and deploy work is another development domain covered by the existing implementation requirements (Requirements 4, 5, and 6).

### Requirement 9: Weekly Review

The weekly review is a per-project maintenance activity run by at least one team member. It performs these concrete actions:

1. **Process the reflexion queue** — for each queued reflexion, classify as strategic or tactical. Route strategic items to deferred ADR tracking. Route tactical items to mulch capture.

2. **Review deferred decisions** — check all tracked ADR needs, spikes, and architectural gaps. For each: confirm it is still relevant, note if it has been resolved by work done since it was tracked, escalate any that are blocking current work. For needs that are ready to be addressed, start a new draft ADR to satisfy them.

3. **Review in-progress ADRs** — for each ADR in draft or proposed status, check if discussion has stalled, check if unread comments exist. Surface what is holding back progress so the reviewer can follow up with the appropriate people out of band.

4. **Capture missed tactical learnings** — review git history for significant changes from the past week that lack corresponding mulch entries.

## Design Notes

These items surfaced during requirements discussion and need to be revisited during design and implementation:

- **ADR supersedes relationship:** The ADR author skill needs to properly support the "supersedes" relationship. When a new ADR overrides an older one, both ADRs should reflect this.

- **Mulch storage location:** Mulch content should live under `.tasty-dev/` for consolidation with ADRs (e.g., `.tasty-dev/mulch/` rather than a separate `.mulch/` directory). This affects how we adopt the mulch CLI.

- **Deferred decision tracking:** Deferred decisions (ADR needs, spikes, tracked gaps) need a persistence mechanism in `.tasty-dev/` checked into the project so any team member can see and follow up on them. Format and structure TBD.

- **Ecosystem health / self-healing:** Individual skills should have ecosystem health properties — detecting when the ecosystem is unhealthy and attempting to correct it (e.g., weekly review overdue, reflexions not firing). This is a property of individual skill execution, not a standalone activity.

- **Telemetry is automatic:** Telemetry recording happens automatically as part of skill execution. It is for the ecosystem author (for validation and refinement), not a user-facing weekly activity.

- **SessionStart hook design:** Tasty-dev needs its own SessionStart hook that coexists with other development skill suites (superpowers, etc.). The hook should establish trigger conditions for the ecosystem without assuming it is the only system shaping behavior. Available hook events include SessionStart, PreToolUse, PostToolUse, and others — the choice of which to use for each requirement should be driven by the specific behavior, not decided in advance.

- **Mulch CLI adoption:** The jayminwest/mulch CLI is the preferred approach for mulch management. It is a zero-network, git-native tool with no privacy concerns. Integration needs to account for: storage location override (`.tasty-dev/mulch/` instead of `.mulch/`), hook coexistence with tasty-dev's own hooks, and the `prime` command as the context delivery mechanism.

- **External skill suite cooperation:** Tasty-dev should cooperate with any development skill suite, not just superpowers. The ecosystem should augment skill dispatch when other suites are present, without requiring those suites to know about tasty-dev.
