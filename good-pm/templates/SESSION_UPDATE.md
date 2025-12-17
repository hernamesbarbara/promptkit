# Session Context Update Instructions

> These instructions are triggered by the Stop hook before ending a conversation.

---

## The Future Self Test

Before saving anything to session context, ask:

**"If I started a new conversation tomorrow, would this information change how I respond?"**

- **YES** → Save it
- **NO** → Don't save it

---

## What TO Capture

Update `.good-pm/session/current.md` with:

### Active Work
- Which spec is currently being worked on
- Which issues are in progress
- Current state of implementation

### Blockers
- External dependencies waiting on others
- Questions that need user clarification
- Technical obstacles discovered

### Decisions Made
- Architectural choices and their rationale
- Trade-offs considered and why one was chosen
- User preferences expressed during the session

### Handoff Notes
- What the next session needs to know to continue
- Any partial work that needs completion
- Important context that isn't captured in checkboxes

---

## What NOT to Capture

These fail the Future Self test:

### Task Completion Logs
- "Completed issue 003" → That's what checkboxes are for
- "Finished implementing the login flow" → Check the boxes

### Session-Specific Research
- API documentation looked up → Store in project docs if needed
- Code patterns discovered → Put in relevant source files

### Git-Recoverable Information
- What files were changed → `git diff` shows this
- When changes were made → `git log` shows this

### Transient Debugging
- Error messages that were fixed
- Temporary workarounds that were resolved

---

## Update Process

1. **Review** current `.good-pm/session/current.md`
2. **Apply** the Future Self test to any new information
3. **Update** only sections that have meaningful changes
4. **Confirm** the update or note that no changes were needed

After updating (or confirming no updates needed), you may complete your response.

---

*This document is auto-injected by the Stop hook to ensure session continuity.*
