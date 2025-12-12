---
description: Set the active project directory for issue tracking commands
argument-hint: <project-path>
allowed-tools: Read, Write, Bash
---

# /set-project

Set the active project directory so that `/issues`, `/fix-issue-status`, `/fix-issue-relationships`, and `issues-housekeeper` automatically use it without requiring a path argument.

**Input:** `$ARGUMENTS` — path to a project directory (e.g., `cybercreds-data/pdf-document-classifier/`)

---

## Instructions

1. **Validate input:**
   - If `$ARGUMENTS` is empty: output `Error: Project path required. Usage: /set-project <project-path>` and stop

2. **Validate the path is a project directory:**
   - Check if the path exists
   - Check if it contains `specs/` and/or `issues/` subdirectories
   - If neither exists: output `Error: {path} doesn't appear to be a project directory (no specs/ or issues/ found)` and stop

3. **Normalize the path:**
   - Convert to absolute path if relative
   - Remove trailing slash for consistency
   - Store the normalized path

4. **Create session directory if needed:**
   - Create `.claude/session/` directory if it doesn't exist

5. **Write the session file:**
   - Write the normalized path to `.claude/session/current-project`
   - The file should contain only the path, no extra formatting

6. **Confirm:**
   - Output: `Project set: {path}`
   - Show a brief summary of what was found:
     - Number of specs in `specs/`
     - Number of issues in `issues/`
   - Remind user: `Run /issues to see status, or /clear-project to unset.`

---

## Examples

```bash
# Set project with relative path
/set-project cybercreds-data/pdf-document-classifier
# Output: Project set: /full/path/to/cybercreds-data/pdf-document-classifier
#         Found: 1 spec, 22 issues
#         Run /issues to see status, or /clear-project to unset.

# Set project with absolute path
/set-project /Users/me/code/myproject
# Output: Project set: /Users/me/code/myproject
#         Found: 2 specs, 15 issues
#         Run /issues to see status, or /clear-project to unset.

# Invalid path
/set-project ./nonexistent
# Output: Error: ./nonexistent doesn't exist

# Not a project directory
/set-project ./some-random-folder
# Output: Error: ./some-random-folder doesn't appear to be a project directory (no specs/ or issues/ found)
```

---

## Session File Location

The active project is stored in: `.claude/session/current-project`

This file is read by:
- `/issues` (when no argument provided)
- `/fix-issue-status` (when no argument provided)
- `/fix-issue-relationships` (when no argument provided)
- `issues-housekeeper` agent (when no path mentioned)

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `/show-project` | Display the currently active project |
| `/clear-project` | Unset the active project |
| `/issues` | Show status (uses active project if set) |
