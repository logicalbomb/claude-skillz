# ADR Author Skill — Development Testing

Development-time validation for the adapted ADR author skill.
These materials are used during skill development and stay in this repo.
They do not ship with the plugin.

## Seed Test Project Setup

Create a temporary test project to exercise review/discussion features:

```bash
# Create test project
mkdir -p /tmp/adr-test-project
cd /tmp/adr-test-project
git init
bin/init-project-storage .
```

### Seed ADR 1: Proposed with Discussion

Write to `.tasty-dev/adr/0001-use-postgresql-for-persistence.md`:

```markdown
---
status: proposed
date: 2026-03-20
decision-makers: [zac, alice]
consulted: []
informed: []
domains: [infrastructure, data]
affects: [backend, deployment]
related: []
supersedes: []
enforces: []
discussion:
  participants: [zac, alice, bob]
  unread_by: [zac]
  started: 2026-03-20
  last_updated: 2026-03-25
---

# Use PostgreSQL for Persistence

## Context and Problem Statement

We need a database for our application. The team has experience with both PostgreSQL and MongoDB, but we need ACID compliance for financial transactions.

## Decision Drivers

* ACID compliance for financial data
* Team familiarity
* Operational simplicity

## Considered Options

* Option 1: PostgreSQL with connection pooling
* Option 2: MongoDB with transactions
* Option 3: CockroachDB for distributed SQL

## Decision Outcome

Chosen option: "Option 1: PostgreSQL with connection pooling", because it provides native ACID compliance with the lowest operational overhead and highest team familiarity.

### Consequences

* Good, because team already knows PostgreSQL well
* Good, because ACID compliance is native, not bolted on
* Bad, because horizontal scaling requires more effort than MongoDB
* Neutral, because connection pooling adds a component to manage

## Pros and Cons of the Options

### Option 1: PostgreSQL with connection pooling

Mature RDBMS with strong ACID support.

* Good, because native ACID compliance
* Good, because team has 5+ years experience
* Good, because excellent tooling ecosystem
* Bad, because horizontal scaling is complex
* Bad, because connection pooling adds operational overhead

### Option 2: MongoDB with transactions

Document database with multi-document transaction support since 4.0.

* Good, because flexible schema for evolving data models
* Good, because built-in horizontal scaling
* Bad, because transaction support is newer and less battle-tested
* Bad, because team has limited MongoDB experience

### Option 3: CockroachDB for distributed SQL

Distributed SQL database with PostgreSQL wire compatibility.

* Good, because horizontal scaling with SQL interface
* Good, because PostgreSQL compatible (familiar syntax)
* Bad, because higher operational complexity
* Bad, because smaller ecosystem and community

## Discussion

### Comment by Alice (2026-03-22 10:30)

I'm concerned about the connection pooling overhead. Have we looked at PgBouncer vs pgpool-II?

#### Reply by Bob (2026-03-25 14:00)

Good point Alice. I've used PgBouncer in production — it's much lighter weight than pgpool-II. I'd recommend PgBouncer in transaction mode.

## More Information
```

### Seed ADR 2: Draft with No Discussion

Write to `.tasty-dev/adr/0002-api-versioning-strategy.md`:

```markdown
---
status: draft
date: 2026-03-25
decision-makers: [zac]
consulted: []
informed: []
domains: [api-design]
affects: [backend, frontend, documentation]
related: []
supersedes: []
enforces: []
discussion:
  participants: [zac]
  unread_by: []
  started: 2026-03-25
  last_updated: 2026-03-25
---

# API Versioning Strategy

## Context and Problem Statement

As we prepare for external API consumers, we need a versioning strategy that allows evolution without breaking existing integrations.

## Decision Drivers

* Backward compatibility for consumers
* Developer experience
* Ease of deprecation

## Considered Options

* Option 1: URL path versioning (/v1/, /v2/)
* Option 2: Header-based versioning (Accept-Version)

## Decision Outcome

Pending — draft for team discussion.

### Consequences

TBD

## Pros and Cons of the Options

### Option 1: URL path versioning

* Good, because immediately visible in URLs
* Good, because simple to implement and route
* Bad, because proliferates URL paths

### Option 2: Header-based versioning

* Good, because cleaner URLs
* Bad, because less discoverable
* Bad, because harder to test in browser

## Discussion

## More Information
```

## Test Scenarios

### Scenario 1: Creation Workflow

**Invoke:** `/adr-author`

**Validate:**
- Project root resolved correctly via `.tasty-dev/config.yaml`
- Next ADR number detected as 0003 (based on seed data)
- Context-aware examples reference existing ADRs (PostgreSQL, API versioning)
- All 9 steps execute in order
- Skeptical review references existing ADR decisions
- Output file is valid MADR with correct frontmatter
- File written to `.tasty-dev/adr/0003-{slug}.md`

### Scenario 2: Review All Unread

**Invoke:** `/adr-author --review`

**Validate:**
- User identity detected from git config
- ADR-0001 shows as needing review (zac in unread_by)
- ADR-0002 is skipped (status: draft)
- Review queue presented correctly
- Comment/reply threading works
- Frontmatter updated after interaction

### Scenario 3: Review Specific ADR

**Invoke:** `/adr-author --review .tasty-dev/adr/0001-use-postgresql-for-persistence.md`

**Validate:**
- ADR loaded and summarized
- All viewing modes work (Chronological, Latest, Full)
- Comment workflow includes critical analysis
- Approval workflow changes status

### Scenario 4: Bootstrap on Fresh Project

**Invoke:** `/adr-author` in a project without `.tasty-dev/`

**Validate:**
- Skill detects missing `.tasty-dev/`
- Offers to run `init-project-storage`
- After init, proceeds with creation workflow
- Generic examples used (no existing ADRs)

## Success Criteria

- Project root resolved via .tasty-dev/config.yaml discovery
- Context-aware examples derived from existing ADRs when present
- Generic examples used when no ADRs exist
- All 9 creation steps complete without hardcoded references
- Review queue correctly identifies unread ADRs
- Comment threading and critical analysis functional
- Approval workflow updates frontmatter status
- No references to core_data_pipeline, Databricks, Unity Catalog, or guardian skills
- Manual commit mode (no auto-commits)
