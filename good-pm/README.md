# Good PM

> Filesystem-based project management for Claude Code with specs, issues, and automatic context injection.

Good PM helps you manage software projects by:
- Creating structured specification documents
- Breaking specs into trackable, numbered issues
- Viewing project status at a glance
- Automatically injecting PM context into conversations

## Installation

Install the plugin from PromptKit:

```bash
claude plugin install good-pm@promptkit
```

Or add manually by copying the `good-pm/` directory to your plugins location.

## Quick Start

```bash
# 1. Initialize Good PM in your project
/good-pm:setup

# 2. Create a specification
/good-pm:create-spec user-auth "OAuth2 authentication with Google and GitHub"

# 3. Break it into trackable issues
/good-pm:create-issues .good-pm/specs/SPEC_user-auth.md

# 4. View project status
/good-pm:issues
```

## Commands

### `/good-pm:setup`

Initialize Good PM in the current repository.

```bash
/good-pm:setup              # Standard setup
/good-pm:setup --force      # Overwrite existing installation
/good-pm:setup --no-settings # Skip hook installation
```

Creates the following structure:

```
.good-pm/
├── context/
│   ├── PM_CONTRACT.md       # Vocabulary and conventions
│   └── session-update.md    # Session update instructions
├── specs/                   # Specification documents
├── issues/                  # Issue files (NNN-description.md)
├── templates/
│   ├── SPEC_TEMPLATE.md
│   └── ISSUE_TEMPLATE.md
├── session/
│   └── current.md           # Current session state
└── INDEX.md                 # Navigation and quick links
```

### `/good-pm:create-spec`

Create a structured specification document.

**From text summary:**
```bash
/good-pm:create-spec api-caching "Redis-based caching layer for API responses"
```

**From draft file:**
```bash
/good-pm:create-spec payment-flow ./notes/payment-draft.md
```

The spec name must be lowercase kebab-case (e.g., `user-auth`, `api-v2`).

### `/good-pm:create-issues`

Break a spec into discrete, numbered issue files.

```bash
/good-pm:create-issues .good-pm/specs/SPEC_user-auth.md
```

Issues are numbered sequentially (001, 002, ...) and placed in `.good-pm/issues/`.

### `/good-pm:issues`

Display status summary of all specs and issues.

```bash
/good-pm:issues              # Current directory
/good-pm:issues ./my-project # Specific project path
```

Status is derived from checkbox state:
- **Open**: No checkboxes checked (0/N)
- **In Progress**: Some checkboxes checked (M/N where 0 < M < N)
- **Complete**: All checkboxes checked (N/N)

## Directory Structure

After running setup and creating specs/issues:

```
your-project/
├── .claude/
│   └── hooks/
│       ├── good-pm-context.sh        # UserPromptSubmit hook
│       └── good-pm-session-update.py # Stop hook
├── .good-pm/
│   ├── context/
│   │   ├── PM_CONTRACT.md
│   │   └── session-update.md
│   ├── specs/
│   │   ├── SPEC_user-auth.md
│   │   └── SPEC_api-caching.md
│   ├── issues/
│   │   ├── 001-setup-database.md
│   │   ├── 002-implement-login.md
│   │   └── 003-add-validation.md
│   ├── templates/
│   │   ├── SPEC_TEMPLATE.md
│   │   └── ISSUE_TEMPLATE.md
│   ├── session/
│   │   └── current.md
│   └── INDEX.md
└── .claude/settings.local.json  # Hook configuration
```

## How It Works

### Automatic Context Injection

The `UserPromptSubmit` hook runs on every prompt submission. If you're in a Good PM project (`.good-pm/` exists), it injects:

1. **PM_CONTRACT.md** - Status vocabulary, frontmatter fields, and conventions
2. **session/current.md** - Current session state and handoff notes (if meaningful content exists)

This ensures Claude always has project management context without manual loading.

### Session Continuity

The `Stop` hook runs when Claude is about to complete a response. It blocks completion until you review the session context, ensuring:

- Active work is documented
- Blockers are noted
- Next steps are captured
- Handoff notes are written for future sessions

The **Future Self Test**: "If I started a new conversation tomorrow, would this information change how I respond?"

### Status Derivation

Status is inferred from checkboxes, not manual tagging:

```markdown
## Tasks
- [ ] Create schema    # Unchecked
- [x] Add migration    # Checked
- [ ] Seed data        # Unchecked
```
Result: **In Progress** (1/3)

## Troubleshooting

### Clear Plugin Cache

If you're developing or updating the plugin and changes aren't appearing:

```bash
# macOS
rm -rf ~/Library/Caches/claude-code/plugins/good-pm*

# Linux
rm -rf ~/.cache/claude-code/plugins/good-pm*
```

Then restart Claude Code.

### Hook Not Firing

1. Check `.claude/settings.local.json` has the hook configuration
2. Verify hook scripts are executable:
   ```bash
   chmod +x .claude/hooks/good-pm-context.sh
   chmod +x .claude/hooks/good-pm-session-update.py
   ```
3. Run `/good-pm:setup --force` to reinstall hooks

### "Good PM is not initialized" Error

Run `/good-pm:setup` in your project directory.

### Context Not Being Injected

The context hook only runs when:
- `.good-pm/` directory exists in current working directory
- `PM_CONTRACT.md` exists in `.good-pm/context/`

Check that you're in the correct directory.

### Session Context Not Updating

The Stop hook requires:
- `.good-pm/session/` directory to exist
- Python 3 available in path

Run `/good-pm:setup --force` to ensure all files are properly installed.

## Workflow Example

1. **Start a new feature**
   ```bash
   /good-pm:create-spec notifications "Real-time push notifications for mobile"
   ```

2. **Review and expand the spec** - Edit `.good-pm/specs/SPEC_notifications.md`

3. **Break into issues**
   ```bash
   /good-pm:create-issues .good-pm/specs/SPEC_notifications.md
   ```

4. **Work through issues** - Check off tasks as you complete them

5. **Check progress**
   ```bash
   /good-pm:issues
   ```

6. **End session** - The Stop hook reminds you to update session context

7. **Next session** - Context is auto-injected, you pick up where you left off

## Version

1.0.0
