---
description: Fix broken references between issues, specs, and README after issues-housekeeper audit
argument-hint: <project-path OR issue-file-path>
allowed-tools: Read, Edit, Glob, Grep
---

# /fix-issue-relationships

## Purpose

Fix broken or missing references between issues, specs, and README. This command ensures the relationship chain is valid:

```
README.md ←→ specs/SPEC_*.md ←→ issues/NNN-*.md
```

Designed to run **after** `issues-housekeeper` identifies relationship problems, and alongside `/fix-issue-status`.

## Typical Workflow

```text
# Full pipeline (single prompt)
> Use issues-housekeeper to audit my-project/ and fix any problems
> using /fix-issue-status and /fix-issue-relationships

# Or step by step
> Use issues-housekeeper to audit my-project/
[Agent reports: 3 orphaned issues, 2 unlinked issues, stale README]

> /fix-issue-relationships my-project/
[Fixes all relationship problems in project]

# Or fix single file
> /fix-issue-relationships my-project/issues/003-broken-ref.md
[Fixes just that one issue's references]
```

---

## Input Modes

| Argument | Mode | Example |
|----------|------|---------|
| `$ARGUMENTS` = project directory | **Project mode** | `/fix-issue-relationships user-auth/` |
| `$ARGUMENTS` = issue file path | **Single file mode** | `/fix-issue-relationships user-auth/issues/003-task.md` |
| `$ARGUMENTS` = empty | **Error** | Prompt user for path |

### Detection Logic

- If `$ARGUMENTS` ends with `.md` → **Single file mode**
- If `$ARGUMENTS` is a directory (or ends with `/`) → **Project mode**
- If `$ARGUMENTS` is empty → Error: `Usage: /fix-issue-relationships {project-path OR issue-file}`

---

## Relationship Types

### 1. Issue → Spec (via `## Source`)

Each issue should have a `## Source` section with a **relative path** from the issue to the spec:

```markdown
## Source
This issue is part of the work defined in: `../specs/SPEC_user-auth.md`
```

The path must be relative from the issue file's location (`{project}/issues/`) to the spec (`{project}/specs/`), so it always starts with `../specs/`.

**Problems to detect:**
- Missing `## Source` section entirely
- Path doesn't resolve to an existing file
- Wrong path format (e.g., `specs/SPEC_*.md` missing `../`, or `issues/specs/...`)
- Referenced file exists but isn't a spec (doesn't match `SPEC_*.md`)
- Referenced spec is from a different project

### 2. Issue → Issue (via `## Dependencies`)

Issues may declare dependencies:

```markdown
## Dependencies
- 001-setup-oauth.md
- 002-google-provider.md
```

Or shorthand:
```markdown
## Dependencies
001, 002
```

**Problems to detect:**
- Referenced issue doesn't exist
- Circular dependencies (A→B→A)
- Dependency in different project

### 3. README → Issues (via issue list)

README should list all issues:

```markdown
## Issues
| # | Issue | Status |
|---|-------|--------|
| 001 | setup-oauth | Complete |
```

**Problems to detect:**
- README lists issue that doesn't exist
- Issue exists but not listed in README
- Issue number/name mismatch

### 4. README → Specs

README should reference the spec(s):

```markdown
## Specs
- [SPEC_user-auth.md](specs/SPEC_user-auth.md)
```

**Problems to detect:**
- README references spec that doesn't exist
- Spec exists but not mentioned in README

---

## Single File Mode

When `$ARGUMENTS` is a file path (e.g., `my-project/issues/003-task.md`):

### Step 1: Validate the file

1. Check file exists
2. Check it's in an `issues/` directory
3. Derive project root (parent of `issues/`)

### Step 2: Parse current references

Read the file and extract:
- `## Source` reference (path to spec)
- `## Dependencies` references (paths/numbers to other issues)

### Step 3: Validate references

For `## Source`:
```
Reference: ../specs/SPEC_new-data-pipeline.md
Resolves to: /full/path/new-data-pipeline/specs/SPEC_new-data-pipeline.md
File exists: Yes/No
Is valid spec: Yes/No (matches SPEC_*.md)
Same project: Yes/No
```

For `## Dependencies`:
```
Dependency: 001
Resolves to: ../001-setup.md or ./001-setup.md
File exists: Yes/No
```

### Step 4: Present findings

```markdown
## Reference Check: 003-clean-new-data.md

### Source Reference
- Current: `../specs/SPEC_new-data-pipline.md`
- Status: BROKEN (file not found)
- Suggestion: `../specs/SPEC_new-data-pipeline.md` (typo in 'pipeline')

### Dependencies
- 001: OK (resolves to 001-setup.md)
- 002: OK (resolves to 002-fetch-data.md)

**Fix source reference?** (Awaiting confirmation)
```

### Step 5: Apply fix (after confirmation)

Update the `## Source` section with corrected path.

---

## Project Mode

When `$ARGUMENTS` is a directory (e.g., `my-project/`):

### Step 1: Discover all files

```
specs/: 2 files
issues/: 15 files
README.md: found
```

### Step 2: Build relationship map

For each issue, parse `## Source` and `## Dependencies`.
Build a graph:

```
SPEC_user-auth.md
  ├── 001-setup-oauth.md ✓
  ├── 002-google-provider.md ✓
  ├── 003-github-provider.md (ORPHANED - references non-existent spec)
  └── 004-session.md (UNLINKED - no Source section)
```

### Step 3: Identify all problems

| File | Problem | Current Value | Suggested Fix |
|------|---------|---------------|---------------|
| 003-github-provider.md | Orphaned | `../specs/SPEC_oauth.md` | `../specs/SPEC_user-auth.md` |
| 004-session.md | Unlinked | (none) | Add `## Source` pointing to `SPEC_user-auth.md` |
| 007-cleanup.md | Broken dep | `006` | `006-validation.md` (file exists) |
| README.md | Missing issue | - | Add 004-session.md to list |
| README.md | Stale entry | 099-old.md | Remove (file doesn't exist) |

### Step 4: Present findings

```markdown
## Relationship Problems: user-auth/

### Orphaned Issues (reference non-existent spec)
| Issue | Current Reference | Suggested Fix |
|-------|-------------------|---------------|
| 003-github-provider.md | `SPEC_oauth.md` | `SPEC_user-auth.md` |

### Unlinked Issues (no Source section)
| Issue | Suggested Spec |
|-------|----------------|
| 004-session.md | `SPEC_user-auth.md` (only spec in project) |

### Broken Dependencies
| Issue | Broken Dep | Fix |
|-------|------------|-----|
| 007-cleanup.md | `006` | `006-validation.md` |

### README Sync Issues
- Missing from README: 004-session.md
- Stale entry in README: 099-old.md (file deleted)

---

**Ready to fix all 5 problems?** (Awaiting confirmation)
```

### Step 5: Apply fixes (after confirmation)

1. Update `## Source` in orphaned/unlinked issues
2. Update `## Dependencies` with correct paths
3. Add missing issues to README
4. Remove stale entries from README

---

## Reference Resolution Logic

### Resolving Source paths

Given an issue at `project/issues/003-task.md` with Source `../specs/SPEC_foo.md`:

1. Start from issue directory: `project/issues/`
2. Apply relative path: `../specs/SPEC_foo.md`
3. Resolve to absolute: `project/specs/SPEC_foo.md`
4. Check file exists
5. Verify filename matches `SPEC_*.md`

### Inferring correct spec

When an issue has no Source or broken Source:

1. Find all specs in `project/specs/`
2. If exactly one spec → suggest that one
3. If multiple specs → check issue filename for hints (e.g., `003-auth-setup.md` might match `SPEC_auth.md`)
4. If ambiguous → flag for manual review, don't auto-fix

### Normalizing paths

Always write Source references as relative paths from issue to spec:

```markdown
## Source
This issue is part of the work defined in: `../specs/SPEC_user-auth.md`
```

Not absolute paths. Not `./`. Just clean relative paths.

---

## Fixing Dependencies

### Format normalization

Accept multiple formats, normalize to consistent style:

```markdown
# Input formats (all valid)
001, 002, 003
001-setup.md, 002-fetch.md
- 001
- 002-setup-oauth.md

# Normalized output
## Dependencies
- 001-setup-oauth.md
- 002-fetch-data.md
```

### Validation

For each dependency:
1. If just a number (`001`), find matching file in `issues/`
2. Verify the file exists
3. Check for circular dependencies

---

## README Sync

### Adding missing issues

If issues exist in `issues/` but not in README:

```markdown
## Issues

| # | Issue | Status | Progress |
|---|-------|--------|----------|
| 001 | setup-oauth | Complete | 5/5 |
| 002 | google-provider | Complete | 3/3 |
+ | 003 | github-provider | Open | 0/4 |  ← Added
```

### Removing stale entries

If README lists issues that don't exist:

```markdown
## Issues

| # | Issue | Status |
|---|-------|--------|
| 001 | setup-oauth | Complete |
- | 099 | old-task | Complete |  ← Removed (file doesn't exist)
```

---

## Integration with Pipeline

This command is designed to work in sequence:

```text
issues-housekeeper → fix-issue-status → fix-issue-relationships
     (diagnose)         (fix status)       (fix references)
```

### Handoff from issues-housekeeper

The agent reports:
- Orphaned issues (Source points to missing spec)
- Unlinked issues (no Source section)
- Broken dependencies
- README sync issues

This command fixes those specific problems.

### Handoff from fix-issue-status

After status is fixed, relationships may still be broken. This command handles the structural integrity.

### Single prompt usage

```text
> Use issues-housekeeper to audit my-project/ and fix any problems
> using /fix-issue-status and /fix-issue-relationships

Claude will:
1. Run issues-housekeeper audit
2. If status problems found → run /fix-issue-status
3. If relationship problems found → run /fix-issue-relationships
4. Report final state
```

---

## Output Contract

### Success (fixes applied)
```
Fixed 5 relationship problems in user-auth/:
- 2 orphaned issues → linked to correct spec
- 1 unlinked issue → added Source section
- 2 README entries → synced

Run issues-housekeeper again to verify.
```

### No problems found
```
No relationship problems found in user-auth/
All issues properly linked to specs.
README is in sync.
```

### Partial fix (some need manual review)
```
Fixed 3 of 5 problems. 2 need manual review:
- 004-ambiguous.md: Multiple specs in project, can't auto-determine
- 007-external.md: References spec in different project (intentional?)
```

---

## Safety

- **Confirmation required** — Always show what will change before modifying
- **Preserve content** — Only modify `## Source`, `## Dependencies`, and README issue list
- **No deletions** — Never delete issue or spec files
- **Ambiguity = manual** — If can't determine correct fix, flag for human review
- **Backup reminder** — Suggest `git diff` after changes to review

---

## Examples

```bash
# Fix single issue
/fix-issue-relationships user-auth/issues/003-broken.md

# Fix whole project
/fix-issue-relationships user-auth/

# Full pipeline
> Use issues-housekeeper to audit data-pipeline/ and fix problems
> with /fix-issue-status and /fix-issue-relationships

# After other fixes
> I just renamed SPEC_old.md to SPEC_new.md, fix the references
> /fix-issue-relationships data-pipeline/
```

---

## What This Command Does NOT Do

- Create new issues or specs
- Delete files
- Fix checkbox status (use `/fix-issue-status` for that)
- Resolve which spec is "correct" when ambiguous
- Fix references across different projects (flags for review instead)

This command **repairs the relationship graph**. It ensures every issue knows its spec, every dependency resolves, and README reflects reality.

---

## Related Tools

| Type | Name | Purpose |
|------|------|---------|
| command | `/issues` | Status summary — see current completion state |
| command | `/create-spec` | Create new spec documents |
| command | `/create-issues` | Break specs into issue files |
| command | `/fix-issue-status` | Sync checkbox state with README |
| agent | `issues-housekeeper` | Validate structure, detect problems |
