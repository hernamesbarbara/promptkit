---
description: Break down a spec into discrete, numbered issue files.
argument-hint: "<path/to/SPEC_name.md>"
---

# Good PM Create Issues

Break a specification document into discrete, trackable issue files in `.good-pm/issues/`.

## Arguments

Parse `$ARGUMENTS` for one positional argument:

- `$1` — **spec-path**: Path to the spec file (e.g., `.good-pm/specs/SPEC_user-auth.md`)

---

## Step 1: Validate Prerequisites

Check that Good PM is initialized:

- If `.good-pm/` directory does NOT exist: **Stop and error**
  - Message: "Good PM is not initialized. Run `/good-pm:setup` first."
- If `.good-pm/templates/ISSUE_TEMPLATE.md` does NOT exist: **Stop and error**
  - Message: "Missing template. Run `/good-pm:setup --force` to reinstall."

---

## Step 2: Validate Spec Path

Validate `$1` (spec-path):

| Rule | Validation |
|------|------------|
| Required | Must not be empty |
| Exists | File must exist at path |
| Format | Should be a `.md` file |

If invalid, **stop and error**:
- Empty: "Spec path is required. Usage: `/good-pm:create-issues .good-pm/specs/SPEC_<name>.md`"
- Not found: "Spec file not found: `<path>`"
- Not markdown: "Expected a markdown file, got: `<path>`"

---

## Step 3: Parse Spec File

Read the spec file and extract:

### 3a. Spec Metadata
- **Title**: Extract from first `# SPEC: <name>` heading or filename
- **Spec name**: Extract from filename (e.g., `SPEC_user-auth.md` → `user-auth`)

### 3b. Implementation Plan
Look for the `## Implementation Plan` section and extract:
- Phase names (from `### Phase N: <name>` headings)
- Tasks within each phase (checkbox items `- [ ]` or `- [x]`)
- Nested tasks (indented checkboxes)

### 3c. Acceptance Criteria
Look for the `## Acceptance Criteria` section and extract:
- All checkbox items as verification points

### 3d. Goals Section
Look for the `## Goals` section and extract:
- Checkbox items representing high-level goals

---

## Step 4: Generate Issues

Transform extracted content into discrete issues:

### 4a. Determine Issue Count and Grouping

Group related tasks into atomic issues. Guidelines:
- Each phase typically becomes 1-3 issues
- Each major goal may become an issue
- Combine tightly coupled tasks
- Keep issues focused (one logical change per issue)

### 4b. Number Issues Sequentially

Determine the next issue number:
1. Scan `.good-pm/issues/` for existing `NNN-*.md` files
2. Find the highest number
3. Start new issues at `highest + 1`
4. If no existing issues, start at `001`

Format: Zero-padded 3 digits (001, 002, ..., 999)

### 4c. Generate Short Descriptions

For each issue, create a kebab-case description:
- Derived from task title or phase name
- Max 50 characters
- Lowercase, `a-z`, `0-9`, `-` only
- Action-oriented (e.g., `setup-database`, `implement-auth-endpoint`)

### 4d. Populate Issue Template

For each issue, read `.good-pm/templates/ISSUE_TEMPLATE.md` and populate:

| Placeholder | Value |
|-------------|-------|
| `{{TITLE}}` | Action-oriented title (verb phrase) |
| `{{SOURCE}}` | Relative path to spec: `../specs/SPEC_<name>.md` |
| `{{TASKS}}` | Checkbox list of tasks for this issue |
| `{{DEPENDENCIES}}` | Previous issue number(s) or "None" |

**Task format:**
```markdown
- [ ] Task description
  - [ ] Subtask if applicable
  - [ ] Another subtask
```

**Dependencies logic:**
- First issue: `None`
- Subsequent issues: Previous issue number (e.g., `001-setup-database`)
- If issues can be parallel: `None` or shared parent

### 4e. Write Issue Files

Write each issue to `.good-pm/issues/NNN-<description>.md`

---

## Step 5: Update INDEX.md

Update `.good-pm/INDEX.md` to reflect new issues:

### 5a. Update Specs Section

If the spec is not already listed, add it:

```markdown
## Specs

| Spec | Status | Issues |
|------|--------|--------|
| [SPEC_user-auth](specs/SPEC_user-auth.md) | Open | 5 |
```

### 5b. Update Issues Section

Replace the "No issues yet" placeholder with an issues table:

```markdown
## Issues

### SPEC_<name>

| # | Title | Status |
|---|-------|--------|
| 001 | Setup database schema | Open |
| 002 | Implement auth endpoint | Open |
| 003 | Add validation middleware | Open |
```

Or append to existing issues section if issues already exist.

---

## Output

After successful creation, print:

```
Created N issues from SPEC_<name>.md:

  001-<description>.md
  002-<description>.md
  003-<description>.md
  ...

Issues written to: .good-pm/issues/
Updated: .good-pm/INDEX.md

View status with:
  /good-pm:issues
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Good PM not initialized | Error: "Run `/good-pm:setup` first." |
| Missing issue template | Error: "Run `/good-pm:setup --force` to reinstall." |
| Empty spec path | Error with usage hint |
| Spec file not found | Error with path |
| Spec has no Implementation Plan | Warning: "No Implementation Plan found. Creating issues from Goals and Acceptance Criteria." |
| Spec has no extractable tasks | Error: "No tasks found in spec. Add an Implementation Plan with checkbox items." |
| Cannot write issue file | Error: "Failed to write issue: `<path>`. Check permissions." |
| Cannot update INDEX.md | Warning: "Issues created but could not update INDEX.md" |

---

## Examples

```bash
# Standard usage
/good-pm:create-issues .good-pm/specs/SPEC_user-auth.md

# From project root
/good-pm:create-issues .good-pm/specs/SPEC_api-caching.md

# After creating a spec
/good-pm:create-spec payment-flow "Stripe integration for subscriptions"
/good-pm:create-issues .good-pm/specs/SPEC_payment-flow.md
```

---

## Issue Generation Guidelines

When breaking down a spec into issues:

1. **Atomic Changes**: Each issue should represent one logical unit of work
2. **Clear Scope**: A developer should be able to complete an issue in one session
3. **Dependencies**: Issues should be orderable (later issues may depend on earlier ones)
4. **Testable**: Each issue should have verifiable acceptance criteria
5. **Action-Oriented**: Titles should start with verbs (Implement, Add, Create, Fix, Update)

**Example breakdown:**

Spec Implementation Plan:
```markdown
### Phase 1: Database Setup
- [ ] Create user schema
- [ ] Add migration scripts
- [ ] Seed test data

### Phase 2: API Endpoints
- [ ] Implement /auth/login endpoint
- [ ] Implement /auth/register endpoint
- [ ] Add JWT token generation
```

Generated Issues:
```
001-setup-user-database.md     (Phase 1 tasks)
002-implement-login-endpoint.md (login + JWT)
003-implement-register-endpoint.md (register)
```
