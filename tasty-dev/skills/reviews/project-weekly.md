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

For strategic items, hand off to the ADR author skill:

Invoke `/adr-author` with the reflexion context pre-loaded. The skill's guided conversation will capture the decision with full context, alternatives, and consequences through its 9-step workflow.

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
