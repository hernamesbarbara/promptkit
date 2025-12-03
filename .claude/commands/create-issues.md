---
description: Break down a spec, PRD, or technical memo into discrete issue files
---

The user wants to break down a document into issues.

**Source document:** $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user to provide a path to the spec, PRD, or technical memo.

## Setup

1. Read the document at `$ARGUMENTS`.
2. Create an `issues/` directory if it doesn't exist.
3. Check if `.gitignore` exists. If it does, check if `issues/` is already ignored. If not, add `issues/` to `.gitignore`.
4. If `$ARGUMENTS` is not already inside `issues/`, move it there. Use the new path for all subsequent references.

## Create Issues

Break the work into discrete, independently-completable issues. Each issue should be small enough to finish in one focused coding session.

For each issue, create a file `issues/NNN-short-description.md` with:

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

After creating all issues, create `issues/README.md` with:

- Title: "Issues"
- Reference to the source document (use the final path after any move)
- List of all issues in recommended execution order
- Dependencies noted for each issue

Usage:

````bash
/create-issues refactor-docs-tools.md
/create-issues docs/prd-new-feature.md
````
