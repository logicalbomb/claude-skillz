---
name: writing-plans-enhanced
description: Enhanced plan writing with ADR and mulch integration
version: 0.1.0
telemetry:
  expected_cadence: on_demand
  expected_participants: all
  health_signals:
    - "should follow brainstorming before implementation"
---

# Enhanced Writing Plans with Accumulated Expertise

This enhances the superpowers writing-plans skill with comprehensive knowledge integration.

**When to use:** When writing implementation plans after brainstorming

## Integration with Standard Plan Writing

**Before writing plan:**

Query both ADRs and mulch extensively:

Read existing ADRs in `PROJECT_ROOT/.tasty-dev/adr/` and mulch in `PROJECT_ROOT/.tasty-dev/mulch/` for relevant context:

- Strategic context: ADRs for feature area and technology decisions
- Tactical patterns: Mulch for domain patterns, testing, and language-specific practices

**Load accumulated expertise:**
- ADRs inform architecture decisions
- Mulch informs implementation details
- Test patterns from mulch
- Configuration patterns from mulch
- Known edge cases from mulch

**During plan writing:**

1. **Every task informed by expertise** - Not just breadcrumbs, full integration
2. **Test patterns** - Use project-specific test patterns from mulch
3. **Configuration** - Reference mulch for setup patterns
4. **Edge cases** - Include known gotchas from mulch
5. **File paths** - Use established project structure

**In plan document:**

Add section after header:

```markdown
## Relevant Knowledge

**ADRs Referenced:**
- ADR-0005: Use REST with OpenAPI spec
- ADR-0012: User data requires authentication

**Mulch Patterns:**
- `testing/api-integration-tests` - Integration test setup
- `config/database-pooling` - DB connection config
- `patterns/error-handling` - Standard error handling

---
```

## Unknown Areas

If plan reveals unknown areas:

1. **Flag explicitly** - "No mulch pattern found for X"
2. **Research** - Agent investigates or asks user
3. **Document decision** - Capture for future mulch
4. **Continue** - Don't block on missing patterns

## Example Integration

Standard plan task:

```markdown
### Task 3: Implement User Endpoint

**Step 1: Write the failing test**

Use project's API test pattern (from mulch `testing/api-integration-tests`):

\`\`\`python
# tests/test_user_api.py
from tests.fixtures import api_client, auth_token

def test_get_user_profile(api_client, auth_token):
    response = api_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert "email" in response.json()
\`\`\`
```

Notice: Test uses established patterns, not generic examples.
