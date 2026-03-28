---
name: tasty-dev
version: 0.1.0
description: Feedback-driven development system with reflexion loops, ADRs, and cross-project learning. Captures insights during development, stores architectural decisions, and enables continuous learning across projects.
---

# Tasty Dev - Feedback-Driven Development System

A meta-learning system that helps you become a better developer by capturing insights, correcting mistakes, and reviewing progress systematically.

## Overview

Tasty-dev implements a feedback-driven development cycle:

1. **Reflexion Loop**: Capture insights and learnings as they happen
2. **Correction Loop**: Identify and fix recurring mistakes or anti-patterns
3. **Review Cycle**: Weekly reviews of both project progress and accumulated knowledge
4. **Knowledge Base**: Structured storage in ADRs (architectural decisions) and mulch (tactical patterns)

## Commands

### `reflect`
Capture a development insight or decision during your workflow.

**Trigger**: Use when you learn something new, make an important decision, or identify a pattern worth remembering.

**Skill**: `reflexion/capture`

### `correct`
Correct a previous decision or pattern that turned out to be wrong.

**Trigger**: Use when you realize a past decision needs revision or when you identify an anti-pattern.

**Skill**: `reflexion/correct`

### `adr-author`
Create or review architecture decision records through guided conversation.

**Trigger**: Use when making architectural decisions, reviewing existing ADRs, or when a reflexion capture escalates to a strategic decision.

**Skill**: `adr/skill`

**Modes**:
- `/adr-author` — Create a new ADR
- `/adr-author --review` — Review all unread ADRs
- `/adr-author --review <file>` — Review a specific ADR

### `review-project`
Run a weekly project review to assess progress and blockers.

**Trigger**: Run at the end of each week to review project status.

**Skill**: `reviews/project-weekly`

### `review-knowledge`
Run a weekly knowledge repository review to consolidate learnings.

**Trigger**: Run weekly to review accumulated insights and identify patterns.

**Skill**: `reviews/knowledge-weekly`

## Hooks

### Reflexion Trigger Detector
**Events**: `tool_result`, `user_message`
**Script**: `hooks/detect_reflexion_triggers.py`

Automatically detects moments during development when a reflexion might be valuable (e.g., after encountering errors, making corrections, or receiving important feedback).

### Weekly Review Nudge
**Events**: `session_start`, `task_complete`
**Script**: `hooks/nudge_weekly_review.py`

Reminds you to run weekly reviews when it's been more than a week since your last project or knowledge review.

## Storage Structure

- `adrs/` - Architectural Decision Records (significant decisions with context)
- `mulch/` - Tactical patterns and quick wins (lightweight insights)
- `reviews/` - Weekly review outputs

## Integration

This plugin enhances the existing superpowers skills with feedback loops, ensuring that insights from one project inform work on future projects.

## Status

**Version**: 0.1.0 (Under Active Development)

Currently implementing core reflexion and review capabilities. Full integration with cross-project learning coming in future releases.
