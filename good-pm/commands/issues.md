---
description: Display status summary of specs and issues based on checkbox state.
argument-hint: "[project-path]"
---

# Good PM Issues

Display a status summary of all specs and issues in a Good PM project by counting checkboxes to derive status.

## Arguments

Parse `$ARGUMENTS` for one optional positional argument:

- `$1` (optional) — **project-path**: Path to project directory. If omitted, uses current directory.

---

## Step 1: Resolve Project Path

1. **If `$1` is provided:** Use it as the project path
2. **If `$1` is empty:** Use current directory (`.`)

Validate the path exists and is a directory.

---

## Step 2: Validate Good PM Installation

Check that Good PM is initialized:

- If `.good-pm/` directory does NOT exist at project path: **Stop and error**
  - Message: "Good PM is not initialized in this directory. Run `/good-pm:setup` first."

---

## Step 3: Discover Files

### 3a. Find Specs

Search for spec files matching: `{project-path}/.good-pm/specs/SPEC_*.md`

For each spec found, record:
- File path
- Spec name (extracted from filename: `SPEC_user-auth.md` → `user-auth`)

### 3b. Find Issues

Search for issue files matching: `{project-path}/.good-pm/issues/NNN-*.md`

Where `NNN` is a zero-padded 3-digit number (001, 002, ..., 999).

For each issue found, record:
- File path
- Issue number (extracted from filename)
- Short description (from filename after number)

### 3c. Handle Empty Project

If no specs AND no issues found:
- Message: "No specs or issues found in `.good-pm/`. Create a spec with `/good-pm:create-spec`."
- Exit early

---

## Step 4: Count Checkboxes

For each spec and issue file, read the content and count:

| Pattern | Meaning |
|---------|---------|
| `- [ ]` | Unchecked task |
| `- [x]` | Checked task (lowercase) |
| `- [X]` | Checked task (uppercase) |

**Regex patterns:**
- Unchecked: `^\\s*-\\s*\\[\\s*\\]`
- Checked: `^\\s*-\\s*\\[[xX]\\]`

Calculate:
- `checked`: Count of checked boxes
- `total`: Count of all boxes (checked + unchecked)
- `progress`: `checked/total` as fraction

---

## Step 5: Derive Status

Apply status logic based on checkbox counts:

| Condition | Status |
|-----------|--------|
| `total == 0` | **No Tasks** |
| `checked == 0` | **Open** |
| `checked == total` | **Complete** |
| `0 < checked < total` | **In Progress** |

---

## Step 6: Map Issue-to-Spec Relationships

For each issue, parse the `## Source` section to find the parent spec:

1. Look for line matching: `This issue is part of the work defined in: \`../specs/SPEC_*.md\``
2. Extract spec name from the path
3. Group issue under that spec

Issues without a valid Source section are marked as **unlinked**.

---

## Step 7: Calculate Spec Aggregates

For each spec with linked issues:

- **Issue count**: Number of linked issues
- **Aggregate progress**: Sum of checked boxes across all linked issues / Sum of total boxes
- **Aggregate status**: Derived from aggregate progress using same rules as Step 5

---

## Step 8: Format Output

Generate markdown output in this format:

```markdown
# {project-name}

## Specs

| Spec | Status | Progress | Issues |
|------|--------|----------|--------|
| SPEC_user-auth | In Progress | 7/12 (58%) | 5 |
| SPEC_api-caching | Open | 0/8 (0%) | 3 |

## Issues

### SPEC_user-auth

| # | Title | Status | Progress |
|---|-------|--------|----------|
| 001 | setup-database | Complete | 3/3 |
| 002 | implement-login | In Progress | 2/5 |
| 003 | add-validation | Open | 0/4 |

### SPEC_api-caching

| # | Title | Status | Progress |
|---|-------|--------|----------|
| 004 | design-cache-layer | Open | 0/3 |
| 005 | implement-redis | Open | 0/5 |

## Unlinked Issues

(none)

## Summary

- **Specs:** 0 complete, 2 in progress, 0 open
- **Issues:** 1 complete, 1 in progress, 4 open
- **Next:** `003-add-validation.md` (first open issue)
```

### Output Adaptations

- If only one spec exists, simplify the display
- If no issues exist for a spec, note it
- If all items are complete, add celebration: "All done!"
- Show "No Tasks" items separately with a note to add checkboxes

---

## Step 9: Identify Next Action

Determine the recommended next issue to work on:

1. Find the first **Open** issue (by number order)
2. If no open issues, find the first **In Progress** issue
3. If all complete, report "All done!"

Include in output:
- `**Next:** \`NNN-description.md\` (first open issue)`

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Good PM not initialized | Error: "Run `/good-pm:setup` first." |
| Path doesn't exist | Error: "Directory not found: `<path>`" |
| Path is not a directory | Error: "Not a directory: `<path>`" |
| No specs or issues | Message with hint to create spec |
| Cannot read file | Warning: "Could not read: `<path>`" (continue with others) |
| Malformed Source section | Mark issue as unlinked |

---

## Examples

```bash
# Current directory
/good-pm:issues

# Specific project path
/good-pm:issues ./my-project

# Absolute path
/good-pm:issues /path/to/project
```

---

## What This Command Does NOT Do

- Modify any files (read-only operation)
- Move completed issues to archive directories
- Fix broken references (use separate fix commands)
- Create missing specs or issues

This command **observes and reports**. It provides a quick-glance view of project status.

---

## Status Derivation Examples

### Example 1: Open Issue
```markdown
## Tasks
- [ ] Create database schema
- [ ] Add migration script
- [ ] Seed test data
```
Result: **Open** (0/3)

### Example 2: In Progress Issue
```markdown
## Tasks
- [x] Create database schema
- [x] Add migration script
- [ ] Seed test data
```
Result: **In Progress** (2/3)

### Example 3: Complete Issue
```markdown
## Tasks
- [x] Create database schema
- [x] Add migration script
- [x] Seed test data
```
Result: **Complete** (3/3)

### Example 4: No Tasks
```markdown
## Tasks
(Tasks will be added during implementation)
```
Result: **No Tasks** (0/0) — Flag for review
