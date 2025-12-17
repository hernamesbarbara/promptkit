---
description: Set up Good PM in the current repo. Run once per project after installing the plugin.
argument-hint: "[--force] [--no-settings]"
---

# Good PM Setup

Initialize the Good PM filesystem-based project management system in the **current repository**.

## Arguments

Parse `$ARGUMENTS` for:
- `--force` — Overwrite existing `.good-pm/` directory and all files
- `--no-settings` — Skip Claude Code hook installation (settings.local.json changes)

---

## Step 1: Check for Existing Installation

Check if `.good-pm/` directory exists:

- If exists AND `--force` is NOT set: **Stop and warn user**
  - Message: "Good PM is already initialized. Use `--force` to overwrite."
- If exists AND `--force` is set: Proceed (will overwrite)
- If does not exist: Proceed

---

## Step 2: Create Directory Structure

Create all required directories:

```
.good-pm/
├── context/
├── specs/
├── issues/
├── templates/
└── session/
```

Also ensure `.claude/hooks/` exists for the hook scripts.

---

## Step 3: Copy PM_CONTRACT.md

Read the bundled PM_CONTRACT.md from this plugin:
- **Source:** `good-pm/templates/PM_CONTRACT.md` (relative to plugin root)

Write it to the project:
- **Destination:** `.good-pm/context/PM_CONTRACT.md`

This is the vocabulary and conventions document that gets auto-injected into conversations.

---

## Step 4: Copy Session Update Instructions

Read the bundled SESSION_UPDATE.md from this plugin:
- **Source:** `good-pm/templates/SESSION_UPDATE.md` (relative to plugin root)

Write it to the project:
- **Destination:** `.good-pm/context/session-update.md`

This document provides instructions for the Stop hook to guide session context updates.

---

## Step 4b: Create Session Context File

Read the bundled SESSION_TEMPLATE.md from this plugin:
- **Source:** `good-pm/templates/SESSION_TEMPLATE.md` (relative to plugin root)

Write it to the project:
- **Destination:** `.good-pm/session/current.md`

This file tracks ephemeral work state and handoff notes between sessions.

---

## Step 5: Copy Templates

Copy the spec and issue templates from this plugin to the project:

| Source (Plugin) | Destination (Project) |
|-----------------|----------------------|
| `good-pm/templates/SPEC_TEMPLATE.md` | `.good-pm/templates/SPEC_TEMPLATE.md` |
| `good-pm/templates/ISSUE_TEMPLATE.md` | `.good-pm/templates/ISSUE_TEMPLATE.md` |

---

## Step 6: Create INDEX.md

Read the bundled INDEX.md from this plugin:
- **Source:** `good-pm/templates/INDEX.md` (relative to plugin root)

Write it to the project:
- **Destination:** `.good-pm/INDEX.md`

---

## Step 7: Install Hooks

**Skip this step if `--no-settings` flag is set.**

### 7a. Copy Hook Scripts

Copy the bundled hook scripts from this plugin:

| Source (Plugin) | Destination (Project) |
|-----------------|----------------------|
| `good-pm/hooks/good-pm-context.sh` | `.claude/hooks/good-pm-context.sh` |
| `good-pm/hooks/good-pm-session-update.py` | `.claude/hooks/good-pm-session-update.py` |

Make them executable:
```bash
chmod +x .claude/hooks/good-pm-context.sh
chmod +x .claude/hooks/good-pm-session-update.py
```

**Note:** Hook registration is handled automatically by the plugin's `hooks.json`. Setup only needs to copy the script files — no changes to `settings.local.json` are needed.

---

## Output

After successful setup, print:

```
Good PM initialized in .good-pm/

Created:
  .good-pm/context/PM_CONTRACT.md
  .good-pm/context/session-update.md
  .good-pm/templates/SPEC_TEMPLATE.md
  .good-pm/templates/ISSUE_TEMPLATE.md
  .good-pm/INDEX.md
  .good-pm/specs/           (empty)
  .good-pm/issues/          (empty)
  .good-pm/session/current.md

[If hooks installed:]
Hooks installed:
  .claude/hooks/good-pm-context.sh       (UserPromptSubmit)
  .claude/hooks/good-pm-session-update.py (Stop)

[If --no-settings:]
Skipped hook script installation (--no-settings flag).

Next steps:
  /good-pm:create-spec <name> "<summary>"   Create your first spec
  /good-pm:issues                           View project status
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| `.good-pm/` exists without `--force` | Error: "Already initialized. Use --force to overwrite." |
| Cannot create directories | Error: "Failed to create directory: [path]. Check permissions." |
| Cannot write files | Error: "Failed to write file: [path]. Check permissions." |
