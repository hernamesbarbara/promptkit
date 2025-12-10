---
description: Break down a spec, PRD, or technical memo into discrete issue files
---

The user wants to break down a document into issues.

**Source document:** $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user to provide a path to the spec, PRD, or technical memo.

## Setup

1. Read the document at `$ARGUMENTS`.
2. **Extract the spec name** from the filename:
   - If filename matches `SPEC_{name}.md`, extract `{name}` (e.g., `SPEC_user-auth.md` → `user-auth`)
   - If filename doesn't match this pattern, derive a kebab-case name from the filename (e.g., `my-feature-prd.md` → `my-feature-prd`)
3. Create a `SPEC_{name}/` directory if it doesn't exist.
4. Check if `.gitignore` exists. If it does, check if `SPEC_*/` pattern is already ignored. If not, add `SPEC_*/` to `.gitignore`.
5. If `$ARGUMENTS` is not already inside `SPEC_{name}/`, move it there. Use the new path for all subsequent references.

## Create Issues

Break the work into discrete, independently-completable issues. Each issue should be small enough to finish in one focused coding session.

For each issue, create a file `SPEC_{name}/NNN-short-description.md` with:

````markdown
## Title
Clear, action-oriented title

## Source
This issue is part of the work defined in: `$ARGUMENTS`

## Description
What needs to be done and why

## Tasks
- [ ] Specific task 1
- [ ] Specific task 2

## Acceptance Criteria
How to verify this issue is complete

## Dependencies
List any issue numbers that must be completed first (or "None")
````

Keep issues atomic–one logical change per issue. Include specific commands, file paths, or content from the source document needed to complete each issue.

## Create Index

After creating all issues, create `SPEC_{name}/README.md` with:

- Title: "Issues for SPEC_{name}"
- Reference to the source document (use the final path after any move)
- List of all issues in recommended execution order
- Dependencies noted for each issue

Usage:

````bash
/create-issues SPEC_user-auth.md
/create-issues docs/SPEC_api-caching.md
````
