---
name: adr-author
description: Guide creation and review of architecture decision records through conversational workflow
version: 0.1.0
telemetry:
  expected_cadence: on_demand
  expected_participants: all
  health_signals:
    - "at least 1 invocation per project per month"
    - "review mode should run within 7 days of a new proposed ADR"
---

# ADR Author Skill

## Purpose

This skill guides the creation and review of Architecture Decision Records (ADRs) through a structured conversational workflow. It:

- Facilitates thoughtful decision-making through guided questions
- Suggests options based on existing ADRs and project context
- Provides skeptical review to challenge decisions before finalization
- Ensures consistency with existing architectural decisions
- Manages asynchronous discussion, review, and approval workflows

## Usage

Invoke this skill in four ways:

```bash
# Create a new ADR
/adr-author

# Review all ADRs needing your attention
/adr-author --review

# Review and discuss specific ADR
/adr-author --review .tasty-dev/adr/0015-some-decision.md
```

**Behavioral modes:**

- **Creation mode** (`/adr-author`): 9-step guided workflow to create new ADR
- **Review all mode** (`/adr-author --review`): Find and review all unread ADRs sequentially
- **Review specific mode** (`/adr-author --review <file>`): Review and discuss one ADR

## Project Root Resolution

Before any ADR operation, resolve the project root:

1. Walk up from the current working directory or run `git rev-parse --show-toplevel` to find a `.tasty-dev/` directory containing `config.yaml`
2. If found: that directory's parent is `PROJECT_ROOT`. All ADR operations use `PROJECT_ROOT/.tasty-dev/adr/`
3. If not found: ask the user if they'd like to initialize tasty-dev storage, then run `bin/init-project-storage PROJECT_ROOT`
4. Cache `PROJECT_ROOT` for the remainder of the session

## Interpreting Bash Code Blocks

Throughout this skill, bash code blocks serve different purposes:

**Commands Claude should execute:**
- Git operations: `git log`, `git status`, `git diff`, `git show`, `git config`
- These commands gather information about the repository state
- Execute these directly using the Bash tool

**Illustrative examples:**
- Examples showing command syntax or patterns (e.g., invocation examples: `/adr-author`, `/adr-author --review`)
- Examples in user conversation flows (e.g., showing what user types)
- These are for documentation purposes only; do not execute

**File operations:**
- References like `cat /path/to/file.md` or `tail -20 /path/to/file.md`
- These indicate Claude should use the Read tool instead of bash commands
- Per CLAUDE.md: Never use `cat`, `tail`, `head`, or similar bash commands for reading files
- Always use the Read tool for file content operations

**When in doubt:** If a bash block is describing what to show users or appears in example conversations, it's illustrative. If it's in a process step telling Claude what to do, execute it (unless it's a file operation, in which case use Read tool).

## Behavior

When invoked, follow this 9-step workflow:

### Step 1: Initialize Context

**Resolve project root** (see Project Root Resolution above).

**Determine next ADR number:**
- Read `PROJECT_ROOT/.tasty-dev/adr/` to find highest numbered ADR file
- Next ADR will be `####` (4-digit zero-padded)

**Identify participants (optional):**

Ask: "Who should participate in reviewing this decision? (optional)"

Provide guidance:
```
You can provide names (first names, nicknames, or full names).
I'll match them against git authors to populate the participants list.

Leave blank to skip - participants will be added as people engage.

Examples: "alice, bob" or "Alice Chen, Bob Smith"
```

If names provided:
1. Get all git authors: `git log --all --format='%an' | sort -u`
2. Fuzzy match each provided name:
   - Case-insensitive matching
   - Match on first name, last name, or full name
   - Extract username as lowercase first word from matched git author
   - Example: "Alice Chen" → username "alice"
   - Show matches for confirmation
3. Confirm matches with user:
   ```
   I found these git authors:
   - alice (Alice Chen)
   - bob (Bob Smith)

   Add them as participants? [Y/N]
   ```
4. If confirmed, set in frontmatter:
   ```yaml
   discussion:
     participants: [alice, bob]
     unread_by: [alice, bob]
     started: {current_date}
     last_updated: {current_date}
   ```

If no names provided or skipped:
```yaml
discussion:
  participants: []
  unread_by: []
  started: {current_date}
  last_updated: {current_date}
```

**Read existing ADRs for context:**
- Use Glob to find ADRs in `PROJECT_ROOT/.tasty-dev/adr/`
- If ADRs exist: read them to understand existing decisions, build context for suggestions and conflict detection
- If no ADRs exist: note this is the first ADR; use generic software engineering examples throughout the workflow (e.g., database selection, API versioning, monorepo vs polyrepo)

### Step 2: Clarify the Decision

Ask two foundational questions:

**Q1: What decision are we making?**
- Example (generic): "Should we use PostgreSQL or DynamoDB for our persistence layer?"
- Example (context-aware, if ADRs exist): Reference a related existing ADR to frame the question

**Q2: What problem does this solve?**
- Example (generic): "We need to choose a database but have conflicting requirements between query flexibility and write throughput."
- Example (context-aware): Reference related patterns from existing ADRs

Capture clear, specific answers before proceeding.

### Step 3: Identify Decision Drivers

Present common decision drivers and let the human select, add, or remove:

```
Which factors are important for this decision?

Common drivers:
- [ ] Clarity: Self-documenting, obvious intent
- [ ] Performance: Query performance, processing speed
- [ ] Cost: Compute cost, storage cost
- [ ] Governance: Compliance, auditability, lineage
- [ ] Team velocity: Ease of development, onboarding
- [ ] Maintainability: Long-term support, evolution

Select applicable drivers or add custom ones:
```

### Step 4: Explore Options

This is a critical step with 5 substeps:

#### 4a. Present Known Options

Ask the user to describe the options they're considering.

If existing ADRs are relevant, reference them:
```
Based on your existing ADRs, I see related decisions:

Option 1: {pattern from existing ADR}
- Established by: ADR-{NNNN} ({title})

Are there other options you want to consider?
```

If no existing ADRs exist, simply ask:
```
What options are you considering? Describe at least two approaches.
```

#### 4b. Offer to Suggest Additional Options

```
Would you like me to suggest additional options based on:
- Related ADRs in this project
- Common patterns for this type of decision
- Trade-offs you may not have considered

[Yes, suggest alternatives] [No, continue with current options]
```

#### 4c. Generate Suggestions (If requested)

Analyze existing ADRs and the project context to generate suggestions:

**Analysis process:**
1. Read related ADRs to identify patterns and precedents
2. Consider common industry approaches for this type of decision
3. Generate 1-3 additional options with rationale

**Example suggestion (context-aware):**
```
Based on ADR-{NNNN} ({title}) and the patterns in this project:

Option 3: {suggested approach}
Source: Extends the pattern established in ADR-{NNNN}
Pros:
- {pro 1}
- {pro 2}
Cons:
- {con 1}
- {con 2}

Rationale: {why this option is relevant given existing decisions}

Does this option make sense for your context? Should we include it?
```

**Example suggestion (generic, no existing ADRs):**
```
Based on common approaches for this type of decision:

Option 3: {suggested approach}
Pros:
- {pro 1}
- {pro 2}
Cons:
- {con 1}

This is a common choice when {context}. Does this option make sense?
```

#### 4d. Validate Suggestions

For each suggestion:
- Explain the rationale and source
- Ask if it's relevant to their context
- Only include options the human validates

#### 4e. Collaborate on Pros/Cons

For each option (both known and suggested):
```
Let's detail Option 1: {name}

Current pros:
- {pro 1}
- {pro 2}

Current cons:
- {con 1}

What would you add or change?
```

#### 4f. Get Recommendation

After analyzing all options:
```
Based on the decision drivers you selected:
- {driver 1} (high priority)
- {driver 2} (medium priority)

I recommend: Option {N} ({name})

Reasoning:
- {reason tied to driver 1}
- {reason tied to driver 2}
- {reason tied to existing ADR precedent, if applicable}

However, Option {M} ({name}) would be preferable if:
- {condition 1}
- {condition 2}

What's your preference?
```

### Step 5: Skeptical Review

This is a critical step with 2 substeps:

#### 5a. Challenge the Decision

Play devil's advocate with 4 specific challenge types:

```
Let me challenge this decision to help you defend it.

Your preference: Option {N} ({name})

**1. Consistency Issue**
   - Does this conflict with any existing ADRs?
   - If existing ADRs reference related patterns, call out specific conflicts
   - If this is the first ADR, consider: does this set a precedent you're comfortable with?

**2. Historical Precedent**
   - Has a similar decision been made before in this project?
   - Check existing ADRs for related decisions and whether this aligns or diverges
   - If no precedent exists, note that this establishes new ground

**3. Foundational Principle Challenge**
   - Does this align with the project's stated principles and decision drivers?
   - Are you trading off a principle you previously prioritized?
   - If so, should you revisit that earlier decision?

**4. Migration Cost**
   - What existing code, configuration, or processes need changing?
   - What are the downstream dependencies?
   - Is the benefit worth the migration effort?
   - Have you estimated the scope of change?

How would you respond to these concerns?
```

**Challenge generation guidelines:**
1. **Consistency Issue**: Identify conflicts with existing ADRs in `PROJECT_ROOT/.tasty-dev/adr/`
2. **Historical Precedent**: Check if past decisions apply differently
3. **Foundational Principle Challenge**: Check against stated decision drivers and earlier ADRs
4. **Migration Cost**: Quantify change impact and question ROI

Let human respond to each challenge. This forces them to defend their decision or reconsider.

#### 5b. Status Decision

After skeptical review:
```
Based on your responses to the challenges, what's the status?

1. **Finalize as proposed**: Write the ADR with your chosen option
2. **Save as draft**: Write ADR with status: draft for later review
3. **Revise options**: Go back to Step 4 to reconsider options

Your choice:
```

### Step 6: Define Metadata

#### 6a. Domains

Suggest domains based on content:
```
This decision affects which architectural domains?

Suggest domains based on the decision content and existing ADRs.
If existing ADRs use domain tags, suggest consistent terminology.

Select applicable or add others:
```

#### 6b. Affects

Identify impacted areas:
```
What areas are affected by this decision?

Suggest affected areas based on the decision content and codebase.

Select applicable or add others:
```

#### 6c. Enforces (Placeholder)

Note: Enforcement rules are not yet active. The `enforces` field in the ADR frontmatter will be populated in a future phase when the tasty-dev enforcement system is built (Phase 2.5). For now, leave the field as an empty list.

#### 6d. Relationships

Identify relationships to other ADRs:
```
Relationships to other ADRs:

Suggested (based on reading existing ADRs in PROJECT_ROOT/.tasty-dev/adr/):
- supersedes: (list any ADRs this replaces)
- related_to: (list any ADRs that address similar concerns)

Modify or add relationships:
```

### Step 7: Consequences

Ask about consequences in three categories:

```
What are the consequences of this decision?

**Good consequences:**
- What benefits does this provide?
- What problems does this solve?

Example: "Consistent API versioning makes integration predictable"

**Bad consequences:**
- What are the downsides?
- What complexity does this introduce?

Example: "Requires all existing endpoints to add version prefix"

**Neutral consequences:**
- What changes but isn't clearly good or bad?

Example: "Changes deployment pipeline to support multiple API versions"

Also consider:
- Migration effort: How much work to implement?
- Learning curve: How long to adopt?
- Tooling impact: What tools need updates?
```

### Step 8: Write ADR File

Generate complete MADR file using the template at `templates/adr-template.md`:

```
I'll create the ADR:

Filename: PROJECT_ROOT/.tasty-dev/adr/####-{slug}.md
Status: {proposed|draft}
```

**MADR format** — use the template from `templates/adr-template.md`, filling in:
- Frontmatter: status, date, decision-makers, consulted, informed, domains, affects, related, supersedes, discussion metadata
- Body: Context from Step 2, drivers from Step 3, options from Step 4, outcome from Steps 4f/5, consequences from Step 7, pros/cons from Step 4e

**Show preview:**
```
Here's the ADR content:

[Show first 30 lines]

...

[Show last 10 lines]

Ready to write to PROJECT_ROOT/.tasty-dev/adr/####-{slug}.md?
[Write file] [Make changes] [Cancel]
```

**Write file** (if approved):
- Use Write tool to create file
- Confirm file written successfully

### Step 9: Maintenance Tasks

After writing ADR:

#### 9a. Update Related ADRs

If the new ADR has relationships to existing ADRs:

```
Should I update related ADRs?

ADR-{NNNN} ({title}):
- Add to "related" frontmatter: ADR-{new number}
- {Any content notes if applicable}

Make these updates?
[Yes] [No] [Let me review first]
```

If approved, use Edit tool to update related ADRs in `PROJECT_ROOT/.tasty-dev/adr/`.

#### 9b. Summary

```
ADR-{NNNN} created: PROJECT_ROOT/.tasty-dev/adr/####-{slug}.md

Files modified:
- Created: .tasty-dev/adr/####-{slug}.md
- Updated: .tasty-dev/adr/{related ADRs if any}

Files are ready for you to commit when ready.
```

## Review Mode

Review mode has two invocation patterns:

### Pattern 1: Review Specific ADR

```bash
/adr-author --review .tasty-dev/adr/0004-some-decision.md
```

**Behavior:** Jump directly to reviewing that specific ADR (see Single ADR Review Workflow below).

### Pattern 2: Review All Unread ADRs

```bash
/adr-author --review
```

**Behavior:** Find and review all ADRs needing attention sequentially.

**Detection logic:**

1. **Get current user identity:**
   ```bash
   git config user.name | awk '{print tolower($1)}'
   ```

2. **Find all ADR files:**
   ```
   Use Glob to find `PROJECT_ROOT/.tasty-dev/adr/*.md` matching pattern `[0-9][0-9][0-9][0-9]-*`
   ```

3. **For each ADR, check if review needed:**
   - Read frontmatter
   - Check: `status != "draft"` (only review proposed/accepted ADRs)
   - Check: `current_user NOT IN discussion.participants` OR `current_user IN discussion.unread_by`
   - If both conditions true, add to review queue

4. **Present queue:**
   ```
   Found 3 ADRs needing your review:
   1. ADR-0004: Bridge Foreign Key Pattern (2 new comments)
   2. ADR-0005: Deferred Promotion Pattern (not yet reviewed)
   3. ADR-0006: Auditability Pattern (4 new comments)

   Starting with ADR-0004...
   ```

5. **Process each ADR sequentially** using Single ADR Review Workflow

**Edge cases:**
- No ADRs need review: "All ADRs are up to date! You've reviewed everything."
- Only draft ADRs exist: "No proposed or accepted ADRs need review yet."
- Git config fails: Ask user for their name

### Single ADR Review Workflow

When reviewing a specific ADR (either from queue or direct invocation):

**Step 1: Present context summary**

```
=== ADR-0004: Bridge Foreign Key Pattern ===
Status: proposed

Summary: Proposes storing Bronze FK references in fact bridge tables
rather than resolved composite keys.

Discussion status: 3 comments, last by Bob on 2026-02-13. You haven't
responded yet.
```

**Step 2: Offer viewing modes**

```
How would you like to review?

[C] Chronological - Step through commit history to see how discussion evolved
[L] Latest - Jump to recent comments
[F] Full - Read entire ADR + all discussion at once
```

**Step 3: Present content based on choice**

- **Chronological**: Use Git History Navigation (see Chronological Navigation section)
- **Latest**: Show recent comments from Discussion section
- **Full**: Display entire ADR file

**Step 4: Offer action menu**

```
What would you like to do?

- Comment or reply
- Approve this ADR
- Ask me (Claude) to analyze something
- Skip to next ADR (if in queue mode)
- Exit review
```

**Step 5: Handle user choice**

- Comment/reply: Go to Comment Workflow (see Comment Review Workflow section)
- Approve: Go to Approval Workflow (see Approval Workflow section)
- Analyze: Activate Claude AI facilitator (see Claude as AI Facilitator section)
- Skip: Mark user as read (remove from unread_by), move to next ADR in queue
- Exit: Mark user as read, end session

## Chronological Navigation (Commit History)

When user chooses **[C] Chronological** viewing mode in review workflow:

**Step 1: Get commit history for this ADR**

```bash
git log --reverse --format='%H|%an|%ad|%s' --date=format:'%Y-%m-%d %H:%M' -- PROJECT_ROOT/.tasty-dev/adr/XXXX-*.md
```

Parse output into list of commits:
```
commit_hash | author_name | date_time | commit_message
```

**Step 2: Start at first commit (or first unreviewed commit)**

If user has never reviewed this ADR:
- Start at first commit (oldest)

If user has reviewed before but there are new commits:
- Jump to first commit after their last review
- How to detect: Check if user_last_review_date exists (future enhancement: store in metadata)
- For initial implementation: Always start at beginning

**Step 3: Present commit navigation interface**

For each commit in sequence:

```bash
# Get file contents at this commit
git show <commit_hash>:.tasty-dev/adr/XXXX-*.md

# Get diff for this commit
git show <commit_hash> -- .tasty-dev/adr/XXXX-*.md
```

Present to user:

```
=== Commit 3/7 by Bob (2026-02-14 14:00) ===
"Add reply about performance benchmarks"

Changes in this commit:
---
#### Reply by Bob (2026-02-14 14:00)

Good point Alice. I ran a quick test and saw similar numbers.
But I agree with Claude - auditability is more important for our use case.
---

Thread context (previous comments in this thread):
---
### Comment by Alice (2026-02-14 10:30)

I'm concerned about the performance implications of Option 1.
Has anyone benchmarked the join overhead?

#### Reply by Claude (AI) (2026-02-14 10:45)

Based on ADR-0001 benchmarks, similar join patterns showed ~50ms
overhead at 10M rows...
---

Navigation: [P] Previous | [N] Next | [L] Latest | [C] Comment | [A] Approve | [S] Skip to next ADR
```

**Step 4: Handle navigation commands**

Track current_commit_index (0-based) for the ADR.

- **P / Previous**: Decrement current_commit_index, show previous commit (if not at start)
- **N / Next**: Increment current_commit_index, show next commit (if not at end)
- **L / Latest**: Set current_commit_index to last, show most recent commit
- **C / Comment**: Save current position, switch to HEAD, enter Comment Workflow
- **A / Approve**: Save current position, enter Approval Workflow
- **S / Skip**: Mark user as read, exit this ADR (move to next in queue if exists)

**Step 5: Resume after commenting**

After user adds comment via [C]:
- File is modified at HEAD
- Ask: "Continue reviewing commit history? [Y/N]"
- If Yes: Return to saved current_commit_index
- If No: Exit to action menu or next ADR

**Step 6: Handle end of history**

When current_commit_index reaches last commit:
```
You've reached the latest changes.

What would you like to do?
- Comment or reply
- Approve this ADR
- Skip to next ADR
- Exit review
```

## Discussion Section Management

### Formatting Rules

All comments and replies follow consistent markdown formatting:

**Top-level comment:**
```markdown
### Comment by [Name] ([YYYY-MM-DD HH:MM])

[Comment content, can be multiple paragraphs]
```

**Reply to comment:**
```markdown
#### Reply by [Name] ([YYYY-MM-DD HH:MM])

[Reply content, can be multiple paragraphs]
```

**AI attribution:**
```markdown
### Comment by Claude (AI) ([YYYY-MM-DD HH:MM])
```

**Rules:**
- Blank line before each comment/reply
- Blank line after each comment/reply
- Date format: `YYYY-MM-DD HH:MM` (24-hour time)
- Name is user's first name (capitalized) or "Claude (AI)"

### Threading Logic

**When to create reply (####) vs new comment (###):**

- **Reply**: User is responding to a specific comment
  - Place immediately after the comment being replied to
  - Use #### heading level
  - Continue the thread

- **New comment**: User is starting a new topic/thread
  - Place after all existing comments/threads
  - Use ### heading level
  - Start fresh discussion

**Claude suggests threading:**
- Analyze user's intent from their words
- "I think..." or "Let me add..." → Likely new comment
- "I agree with X" or "In response to Y" → Likely reply
- Ask for confirmation: "Should this be a reply to Alice's comment, or a new comment? [R/N]"

### Adding Comments to ADR Files

**Process:**

1. **Read current ADR file**
   Use Read tool to read the ADR file at `PROJECT_ROOT/.tasty-dev/adr/XXXX-*.md`

2. **Find Discussion section**
   - Search for `## Discussion` heading
   - If not found, add it at end of file before adding comment

3. **Determine insertion point**
   - For replies: After the comment being replied to, before next ###
   - For new comments: At end of Discussion section

4. **Format new comment/reply**
   ```markdown

   ### Comment by Zac (2026-02-14 16:30)

   [User's comment content]
   ```

5. **Insert into file**
   - Use Edit tool to insert at correct position
   - Maintain blank lines for readability

6. **Update frontmatter metadata**
   - Add user to `participants` if not present
   - Set `unread_by` to all participants except current user
   - Update `last_updated` to current timestamp

7. **Verify modification**
   Use Read tool to verify the last 20 lines of the ADR file at `PROJECT_ROOT/.tasty-dev/adr/XXXX-*.md`

## Comment Review Workflow

Before any comment is posted, Claude performs critical review (similar to Step 5 skeptical review).

### When User Wants to Comment

**Step 1: Capture user's intent**

User says what they want to comment. Examples:
- "I want to comment that Option 2 is better"
- "Reply to Alice that I agree"
- "Add my approval"

**Step 2: Determine threading**

Ask if not clear:
```
Should this be:
[R] Reply to Alice's comment about performance
[N] New comment (separate thread)
```

**Step 3: Draft the comment**

Format as it would appear in ADR:

```markdown
### Comment by Zac (2026-02-14 16:30)

I think Option 2 is better because it's simpler.
```

**Step 4: Perform critical analysis**

Analyze draft for:

1. **Strength check**
   - Is the argument clear and specific?
   - Does it reference concrete evidence (ADRs, benchmarks, requirements)?
   - Is it vague or unsupported?

2. **Contribution check**
   - Has this point already been made by someone else?
   - Does this add new information or perspective?
   - Is it redundant?

3. **Consistency check**
   - Does this conflict with existing ADRs?
   - Does it contradict earlier decisions?
   - Are there missing considerations?

**Step 5: Present analysis and options**

```
Here's what you're about to say:

---
### Comment by Zac (2026-02-14 16:30)

I think Option 2 is better because it's simpler.
---

Let me challenge this:

**Strength check:**
- Your point about simplicity is valid, but vague
- What does "simpler" mean in this context? Fewer components? Less code? Easier to understand?
- Consider referencing concrete evidence from existing ADRs or project metrics

**Contribution check:**
- Bob already made a similar point about ease of implementation
- Your comment doesn't add new information
- Consider: What unique perspective do you bring?

**Alternatives:**
A. Don't comment - Bob's point covers this
B. Strengthen: "Option 2 is simpler from a *data modeling* perspective..."
C. Redirect: "I'm more concerned about the migration cost..."

What would you like to do?
[R] Revise | [P] Post as-is | [X] Cancel | [+] Let Claude add analysis
```

**Step 6: Handle user choice**

- **[R] Revise**: User refines comment, return to Step 3 for new draft
- **[P] Post as-is**: Proceed to add comment to ADR file (no changes)
- **[X] Cancel**: Discard comment, return to action menu
- **[+] Let Claude add analysis**:
  - Post user's comment as-is
  - Add separate Claude (AI) comment with technical context
  - Example: Cross-reference to conflicting ADR, provide benchmark data, etc.

**Step 7: Add comment to file**

If approved (P or +):
- Insert comment into Discussion section (see Discussion Section Management)
- Update frontmatter metadata
- Confirm: "Comment added. Continue reviewing? [Y/N]"

## Approval Workflow

Users can approve ADRs at any time during review.

### Triggering Approval

Approval can be triggered from:
- Navigation menu: `[A] Approve` during chronological navigation
- Action menu: "Approve this ADR" option after viewing
- Direct command: User says "I want to approve this"

### Approval Process

**Step 1: Confirm intention**

```
You're approving ADR-{NNNN}: {Title}

This will:
- Change status from "proposed" to "accepted"
- Update last_updated timestamp
- Add all other participants to unread_by (so they see it's been approved)
- Optionally add an approval comment to discussion

Would you like to:
[A] Approve silently (just change status)
[C] Approve with comment (explain your approval)
[X] Cancel
```

**Step 2a: Silent Approval**

If user chooses [A]:

1. Edit frontmatter:
   ```yaml
   status: accepted
   ```

2. Update discussion metadata:
   ```yaml
   discussion:
     participants: [alice, bob, zac]
     unread_by: [alice, bob]  # All except approver
     started: 2026-02-13
     last_updated: 2026-02-14  # Current timestamp
   ```

3. No changes to Discussion section

4. Confirm: "ADR-{NNNN} approved. Status changed to accepted."

**Step 2b: Approval with Comment**

If user chooses [C]:

1. Ask: "What would you like to say about your approval?"

2. Draft approval comment:
   ```markdown
   ### Comment by Zac (2026-02-14 17:00)

   [User's approval reasoning]
   ```

3. Run through Comment Review Workflow (see Comment Review Workflow section)

4. If comment approved, add to Discussion section

5. Edit frontmatter (same as silent approval):
   - Change status to "accepted"
   - Update discussion metadata

6. Confirm: "ADR-{NNNN} approved with comment. Status changed to accepted."

### Approval Semantics

**Important notes:**

- **No special authority required**: Any participant can approve
- **Multiple approvals allowed**: Each approval is a status update + optional comment
- **Last approval wins**: Status stays "accepted" after multiple approvals
- **Git history shows consensus**: `git log` reveals who approved when
- **Can approve from any status**: "proposed" → "accepted" or "draft" → "accepted"

### Post-Approval Actions

After approval:

```
ADR-{NNNN} is now accepted.

What would you like to do next?
- Review next ADR (if in queue mode)
- Add another comment to this ADR
- Exit review
```

## Claude as AI Facilitator

Claude actively participates in discussions by providing technical analysis and catching issues.

### When Claude Adds Comments

Claude proactively suggests adding comments in these situations:

**1. Detecting conflicts with existing ADRs**

While user is reviewing, Claude analyzes the discussion and current option preferences.

If Claude detects conflict:
```
I notice something: Option 2 conflicts with ADR-{NNNN} ({title}),
which established {principle}. Option 2 diverges from that decision.

Would you like me to add this as a comment? [Y/N]
```

If user approves:
```markdown
### Comment by Claude (AI) (2026-02-14 16:45)

I notice Option 2 conflicts with ADR-{NNNN} ({title}), which
established {principle}. Option 2 diverges from that decision.
Should we reconsider or amend ADR-{NNNN}?
```

**2. Providing relevant data/context**

When discussion mentions benchmarks, performance, or specific requirements:

```
I found relevant data: ADR-{NNNN} includes information relevant to this
discussion that may inform the decision.

Would you like me to add this as a comment? [Y/N]
```

**3. Identifying missing considerations**

If discussion is one-sided or missing key factors:

```
This discussion hasn't addressed {missing consideration} yet.
Based on the project context, this could be relevant.

Should I mention this in the discussion? [Y/N]
```

### When Claude Stays Quiet

Claude does NOT add comments when:
- Discussion is healthy and covering all bases
- Points being made are clear and don't need technical backup
- **Topic is already covered by existing comments** (no repetition)
- User specifically says "Claude, stay quiet for now"

### Pre-Comment Checks

Before suggesting any comment, Claude must verify:

1. Has this point already been made by someone else?
2. Does this add new technical information or perspective?
3. Is this relevant to the current discussion thread?
4. Only suggest if it contributes something new

### User Control

**Prompt Claude explicitly:**
```
User: "Claude, what do you think about Option 3?"
User: "Claude, analyze the performance implications"
```

Claude responds with analysis and offers to add as comment.

**Suppress Claude:**
```
User: "Claude, stay quiet for now"
User: "Claude, no comments from you on this one"
```

Claude only responds when explicitly asked.

### Claude Comment Format

All Claude comments follow same format as human comments:

```markdown
### Comment by Claude (AI) (2026-02-14 16:45)

[Concise technical analysis, 2-3 sentences maximum]

Reference specific ADRs, data, or patterns when possible.
```

**Keep it concise:**
- 2-3 sentences maximum
- Reference concrete sources (ADR-XXXX, benchmark data, requirements docs)
- Only add when providing technical insight user might miss

## Git Commit Workflow

**Default behavior: Manual commits**

Per user's preferences in CLAUDE.local.md, Claude does NOT automatically commit changes.

### Manual Commit Mode (Default)

**Behavior:**

1. Claude edits ADR files (adds comments, updates metadata)
2. Claude does NOT run `git add` or `git commit`
3. User can add multiple comments across multiple ADRs in single session
4. At end of session, Claude summarizes changes:

```
Session complete. Modified files:
- .tasty-dev/adr/0004-some-decision.md (added 2 comments)
- .tasty-dev/adr/0005-another-decision.md (added 1 comment, approved)

Files are ready for you to commit when ready.
```

5. User commits manually with their preferred workflow

### Verification Before Summary

At end of session, Claude should:

```bash
# Show what changed
git status .tasty-dev/adr/
git diff .tasty-dev/adr/*.md
```

Present summary of modifications to user.

### If User Requests Auto-Commit

If user explicitly requests automatic commits during session:

```
User: "Claude, commit after each comment"
```

Claude can then use git commands (per user permission), but should:
- Commit per ADR (not per comment)
- Use descriptive commit messages
- Include Co-Authored-By trailer
- Never push (user pushes manually)

**Example auto-commit message:**
```bash
git add .tasty-dev/adr/0004-some-decision.md
git commit -m "feat(adr): add discussion comments to ADR-0004

Added 2 comments and 1 reply to discussion.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

**Claude NEVER automatically pushes.**

## Notes

- **Dynamic path resolution**: Always resolve `PROJECT_ROOT` via `.tasty-dev/config.yaml` discovery at session start (see Project Root Resolution)
- **Context-aware examples**: When existing ADRs are present, derive examples and suggestions from them. When none exist, use generic software engineering examples.
- **Skeptical review is mandatory**: Don't skip Step 5a challenges
- **Suggestion engine is optional**: Only run Step 4c if human requests it
- **Be conversational**: This is a guided conversation, not a form to fill out
- **One step at a time**: Don't rush through steps; ensure clarity before proceeding
- **Save progress**: If conversation is interrupted, human can resume with `--review`
- **Enforces field**: Leave as empty list until Phase 2.5 enforcement system is built

## User Identity Detection

Claude must identify the current user to track participation and unread status in ADR discussions.

**When to detect:**
- At skill invocation (Step 1) before any discussion operations
- Cache identity for the entire session

**Detection process:**

1. **Get git user name:**
   Run `git config user.name`

2. **Extract first name:**
   - Take first word from git user name
   - Convert to lowercase
   - Example: "Zac Propersi" → "zac"
   - If empty or unset, proceed to fallback

3. **Use throughout session:**
   - When adding comments: attribute to this user
   - When marking as read: remove from unread_by
   - When checking unread: look for this user in unread_by

**Fallback:**
- If git config fails or returns empty, ask: "What name should I use for you in discussions?"
- Extract first word from provided name and convert to lowercase
- Example: User provides "John Smith" → use "john"

**Matching against participants:**
- Case-insensitive comparison on first word only
- Example: detected "zac" matches participant "Zac", "zac", "Zac Propersi", "ZAC"
- If detected user not in participants list, add them automatically when they first comment

**Error handling:**
- If user provides empty response to fallback: re-prompt
- If extraction yields empty string: default to "unknown" and warn user

## Example Invocations

### Creating new ADR from scratch

```
User: /adr-author
Claude: I'll help you create a new ADR. Let me start by finding your project's ADR directory...

[Resolves PROJECT_ROOT via .tasty-dev/config.yaml]
[Reads existing ADRs, determines next number is 0003]

We'll create ADR-0003.

Who should participate in reviewing this decision? (optional)

You can provide names (first names, nicknames, or full names).
I'll match them against git authors to populate the participants list.

Leave blank to skip - participants will be added as people engage.

User: alice, bob

Claude: [Runs git log --all --format='%an' | sort -u]

I found these git authors:
- alice (Alice Johnson)
- bob (Bob Martinez)

Add them as participants? [Y/N]

User: Y

Claude: Great. Now, what decision are we making?

[... rest of 9-step workflow continues ...]
```

### Reviewing unread ADRs

```
User: /adr-author --review

Claude: Let me find ADRs needing your review...

[Detects user identity: "zac" from git config]
[Scans PROJECT_ROOT/.tasty-dev/adr/ for unread ADRs]

Found 2 ADRs needing your review:
1. ADR-0001: Use PostgreSQL for Persistence (3 comments, last by Bob)
2. ADR-0002: API Versioning Strategy (not yet reviewed)

Starting with ADR-0001...

=== ADR-0001: Use PostgreSQL for Persistence ===
Status: proposed

Summary: Proposes PostgreSQL with connection pooling for the
application persistence layer.

Discussion status: 3 comments, last by Bob on 2026-03-20.
You haven't responded yet.

How would you like to review?
[C] Chronological | [L] Latest | [F] Full

[... review workflow continues ...]
```

### Reviewing a specific ADR

```
User: /adr-author --review .tasty-dev/adr/0001-use-postgresql-for-persistence.md

Claude: [Reads ADR, parses frontmatter and discussion]

=== ADR-0001: Use PostgreSQL for Persistence ===
Status: proposed

Summary: Proposes PostgreSQL with connection pooling for the
application persistence layer.

How would you like to review?
[C] Chronological | [L] Latest | [F] Full

[... review workflow continues ...]
```

## Telemetry

After completing this workflow (whether successful, abandoned, or errored):

1. Check if `~/.tasty-dev/config.toml` exists and has `telemetry.enabled = true`
2. If disabled or missing, skip silently
3. If enabled, collect the following trace data:
   - Skill name, version, and mode (create/review/review-specific)
   - Project git remote and user identity
   - Step-level completion status for each workflow step executed
   - Outcome summary (ADRs created/reviewed, comments added, status changes)
   - Any issues (skipped steps, parse errors, user abandonment)
4. Write trace by piping JSON to `bin/write-telemetry-trace`:

```bash
echo '{"skill": "adr-author", "skill_version": "0.1.0", ...}' | bin/write-telemetry-trace
```

5. Do not let telemetry errors interrupt the user's workflow — if writing fails, continue silently

**What to capture in steps:**
- [completed] / [skipped] / [abandoned] status for each major step
- For creation mode: Steps 1-9, noting which were skipped or revised
- For review mode: queue building, each ADR reviewed, comments, approvals
- Critical analysis results (strength/contribution/consistency pass/fail)
- User actions at decision points (posted as-is, revised, cancelled)
