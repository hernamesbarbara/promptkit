---
description: Display the currently active project directory
argument-hint:
allowed-tools: Read
---

# /show-project

Display the currently active project directory set via `/set-project`.

---

## Instructions

1. **Check for session file:**
   - Look for `.claude/session/current-project`
   - If file doesn't exist: output `No active project set. Use /set-project <path> to set one.` and stop

2. **Read and validate:**
   - Read the path from the session file
   - Verify the path still exists
   - If path no longer exists: output `Warning: Active project path no longer exists: {path}` and suggest running `/clear-project`

3. **Display project info:**
   - Output: `Active project: {path}`
   - Show summary:
     - Number of specs in `specs/`
     - Number of issues in `issues/`
   - Remind user of available actions

---

## Output Format

```markdown
Active project: /path/to/cybercreds-data/pdf-document-classifier

Contents:
- 1 spec in specs/
- 22 issues in issues/

Commands that will use this project:
- /issues
- /fix-issue-status
- /fix-issue-relationships
- issues-housekeeper agent

To change: /set-project <new-path>
To clear: /clear-project
```

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `/set-project` | Set the active project |
| `/clear-project` | Unset the active project |
| `/issues` | Show status (uses active project if set) |
