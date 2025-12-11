---
description: Reconcile issue checkbox status with README and spec after issues-housekeeper audit
argument-hint: <project-path>
allowed-tools: Read, Edit, Glob, Grep
---

# /fix-issue-status

## Purpose

Fix discrepancies between issue checkbox status, README completion claims, and spec status. This command is designed to run **after** `/issues` shows status discrepancies or after `issues-housekeeper` finds README sync problems.

Typical workflow:
```
1. User: "/issues my-project/"
2. Command: Shows status with discrepancies (README says complete, checkboxes say otherwise)
3. User: "/fix-issue-status my-project/"
4. Command: Reconciles and fixes status across all files
```

## Input

| Argument | Format | Required |
|----------|--------|----------|
| `$ARGUMENTS` | Project path | Yes |

Example: `/fix-issue-status user-auth/` or `/fix-issue-status cybercreds-data/audit-firm-extraction/`

## Expected Structure

```
{project}/
    ├── README.md           # Contains issue list with completion status
    ├── specs/
    │   └── SPEC_*.md       # Specs with acceptance criteria checkboxes
    └── issues/
        ├── 001-*.md        # Issues with task checkboxes
        ├── 002-*.md
        └── ...
```

---

## Step 1: Validate Project Path

1. If `$ARGUMENTS` is empty: output `Error: Project path required. Usage: /fix-issue-status {project-path}` and stop
2. If `$ARGUMENTS/README.md` doesn't exist: output `Error: No README.md found in $ARGUMENTS` and stop
3. If neither `$ARGUMENTS/specs/` nor `$ARGUMENTS/issues/` exists: output `Error: $ARGUMENTS doesn't appear to be a valid project directory` and stop

---

## Step 2: Gather Current State

### 2a. Parse README for completion claims

Read `$ARGUMENTS/README.md` and find the issues section. Look for patterns like:

```markdown
## Issues

- [x] 001-setup-oauth - Complete
- [x] 002-google-provider - Complete
- [ ] 003-github-provider - In progress
```

Or table format:
```markdown
| Issue | Status |
|-------|--------|
| 001-setup-oauth | Complete |
| 002-google-provider | Complete |
```

Extract: `{issue_number: readme_status}` where status is `complete`, `in-progress`, or `open`.

### 2b. Parse issue files for checkbox state

For each file in `$ARGUMENTS/issues/NNN-*.md`:

1. Count `- [x]` (completed tasks)
2. Count `- [ ]` (incomplete tasks)
3. Determine status:
   - `complete`: all checked (and has checkboxes)
   - `in-progress`: some checked, some not
   - `open`: none checked (or no checkboxes)

Extract: `{issue_number: {checkbox_status, completed, total}}`

### 2c. Parse specs for acceptance criteria

For each file in `$ARGUMENTS/specs/SPEC_*.md`:

1. Find the `## Acceptance Criteria` section
2. Count checkboxes in that section
3. Record: `{spec_name: {completed, total, status}}`

---

## Step 3: Identify Discrepancies

Compare README claims vs issue checkbox reality:

| Issue | README Says | Checkboxes Say | Discrepancy |
|-------|-------------|----------------|-------------|
| 001 | complete | complete | None |
| 002 | complete | open (0/5) | README ahead |
| 003 | open | complete (5/5) | Checkboxes ahead |

Categorize discrepancies:

- **README ahead**: README says complete, but checkboxes show incomplete
  - Likely cause: Work done, checkboxes never updated
  - Fix: Update checkboxes to match README

- **Checkboxes ahead**: Checkboxes complete, but README shows incomplete
  - Likely cause: README never updated after completing work
  - Fix: Update README to match checkboxes

---

## Step 4: Present Findings and Get Approval

Output a summary:

```markdown
## Status Discrepancies Found

### README claims complete, checkboxes incomplete (39 issues)
These issues are marked complete in README but have unchecked boxes:
- 001-setup-oauth.md (0/5 checked)
- 002-google-provider.md (0/3 checked)
- ...

**Recommended action:** Mark all checkboxes as complete in these issues.

### Checkboxes complete, README shows incomplete (0 issues)
None found.

### Other issues
- 6 issues have non-standard filenames (P5/P6 prefix)
- 1 gap in sequence (missing 032)

---

**Ready to fix?**
1. Update 39 issue files to mark all checkboxes complete
2. Update spec status fields based on issue completion
3. Regenerate README issue list

Proceed? (Awaiting confirmation)
```

**STOP and wait for user confirmation before proceeding.**

---

## Step 5: Apply Fixes

After user confirms, apply fixes in this order:

### 5a. Fix issue checkboxes

For each issue where README says complete but checkboxes don't:

```markdown
# Before
- [ ] Task 1
- [ ] Task 2

# After
- [x] Task 1
- [x] Task 2
```

Use Edit tool to replace `- [ ]` with `- [x]` in the `## Tasks` section.

### 5b. Update spec status fields

For each spec, determine new status based on linked issues:

- If all linked issues complete → `**Status:** Complete`
- If some linked issues complete → `**Status:** In Progress`
- If no linked issues complete → `**Status:** Draft`

Update the `**Status:**` line in each spec.

### 5c. Regenerate README issue list

Replace the issues section in README with accurate status:

```markdown
## Issues

| # | Issue | Status | Progress |
|---|-------|--------|----------|
| 001 | setup-oauth | Complete | 5/5 |
| 002 | google-provider | Complete | 3/3 |
| 003 | github-provider | In Progress | 2/4 |
| 004 | session-management | Open | 0/6 |

**Summary:** 2 complete, 1 in progress, 1 open
```

---

## Step 6: Report Results

```markdown
## Fix Complete

### Changes Made
- Updated checkboxes in 39 issue files
- Updated status in 2 spec files
- Regenerated README issue list

### Current State
| Status | Count |
|--------|-------|
| Complete | 43 |
| In Progress | 1 |
| Open | 1 |

### Spec Status
| Spec | Status |
|------|--------|
| SPEC_audit-firm-pdf-extraction.md | In Progress (77%) |
| SPEC_enhance-categorize-documents.md | Draft |

Run `issues-housekeeper` again to verify all discrepancies resolved.
```

---

## Edge Cases

### No README issue list
If README doesn't have an issue list section, add one:
```markdown
## Issues

[Generated issue list here]
```

### Conflicting signals
If both README and checkboxes are incomplete but file was modified long ago, flag for manual review rather than auto-fixing.

### Non-standard issue filenames
Report but don't auto-fix. Offer as separate action:
```
6 issues have non-standard names. Run /fix-issue-status --rename to normalize?
```

### Missing Source references
If issues don't have `## Source` linking to a spec, report but don't block fixes.

---

## Safety

- **Always show changes before applying** — Never modify files without confirmation
- **Preserve content** — Only modify checkbox state and status fields, never delete content
- **Backup suggestion** — Recommend `git status` check before bulk changes
- **Atomic sections** — Only modify specific sections (Tasks, Status, Issues list)

---

## Examples

```bash
# Basic usage after audit
/fix-issue-status user-auth/

# With full path
/fix-issue-status cybercreds-data/audit-firm-extraction/

# Typical workflow
> Use issues-housekeeper to audit data-pipeline/
[Agent reports 15 checkbox discrepancies]
> /fix-issue-status data-pipeline/
[Command fixes all 15, updates README]
```

---

## What This Command Does NOT Do

- Rename files (use `--rename` flag for that, or do manually)
- Delete issues or specs
- Create new issues
- Determine if work is *actually* done — it trusts README or checkboxes as source of truth
- Fix circular dependencies or blocked status

This command **synchronizes status markers**. It assumes the README reflects reality when there's a discrepancy (since humans typically update README more often than individual checkboxes).

---

## Related Tools

| Type | Name | Purpose |
|------|------|---------|
| command | `/issues` | Status summary — see current completion state |
| command | `/create-spec` | Create new spec documents |
| command | `/create-issues` | Break specs into issue files |
| command | `/fix-issue-relationships` | Fix broken Source/dependency references |
| agent | `issues-housekeeper` | Validate structure, detect problems |
