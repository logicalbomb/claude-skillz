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

Read existing ADRs in `PROJECT_ROOT/.tasty-dev/adr/` for relevant decisions.

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
