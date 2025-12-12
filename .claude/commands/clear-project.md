---
description: Unset the active project directory
argument-hint:
allowed-tools: Read, Bash
---

# /clear-project

Clear the active project directory, so issue tracking commands will require explicit paths again.

---

## Instructions

1. **Check for session file:**
   - Look for `.claude/session/current-project`
   - If file doesn't exist: output `No active project was set.` and stop

2. **Read current value for confirmation:**
   - Read the path from the session file before deleting

3. **Delete the session file:**
   - Remove `.claude/session/current-project`

4. **Confirm:**
   - Output: `Cleared active project: {path}`
   - Remind user: `Issue commands now require explicit paths.`

---

## Examples

```bash
# Clear when project is set
/clear-project
# Output: Cleared active project: /path/to/cybercreds-data/pdf-document-classifier
#         Issue commands now require explicit paths.

# Clear when no project set
/clear-project
# Output: No active project was set.
```

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `/set-project` | Set the active project |
| `/show-project` | Display the currently active project |
| `/issues` | Show status (requires path after clearing) |
