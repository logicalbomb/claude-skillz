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
