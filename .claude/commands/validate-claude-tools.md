---
description: Validate Claude tools in .claude/ against Anthropic best practices. Optionally pass a specific path to validate.
---

Validate Claude AI tools against Anthropic's official documentation and best practices.

**Target:** $ARGUMENTS (if empty, validate all of `.claude/`)

## Setup

1. If `$ARGUMENTS` is provided, validate only that path
2. If `$ARGUMENTS` is empty, validate the entire `.claude/` directory
3. Create output file: `CLAUDE_MEMO_AI_TOOLS_REVIEW.md` in the project root

## Validation Framework

For each tool type, check the applicable rules below.

### Skills (`.claude/skills/*/SKILL.md`)

**Structure validation:**
- [ ] SKILL.md exists in skill directory
- [ ] YAML frontmatter has opening and closing `---` delimiters
- [ ] Required field: `name` (lowercase, numbers, hyphens only, max 64 chars)
- [ ] Required field: `description` (non-empty, max 1024 chars, no XML tags)
- [ ] No reserved words in name: "anthropic", "claude"

**Naming convention:**
- [ ] Directory name matches `name` field in frontmatter
- [ ] Name uses gerund form (verb + -ing): e.g., `writing-documentation` not `docs-writer`

**Best practices:**
- [ ] Description includes both what the skill does AND when to use it
- [ ] Description includes trigger phrases/keywords users would say
- [ ] SKILL.md body is under 500 lines
- [ ] Progressive disclosure: explicit "Read X when Y" instructions for bundled files
- [ ] References to other files use forward slashes (not backslashes)
- [ ] If scripts exist, SKILL.md explains when to run vs read them
- [ ] Feedback loops documented if validation scripts exist
- [ ] No time-sensitive information that will become outdated

**File validation:**
- [ ] All internal markdown links resolve to existing files
- [ ] All referenced scripts exist and have valid syntax
- [ ] No placeholder text: `[TODO]`, `[PLACEHOLDER]`, `TBD`, `xxx`
- [ ] Code blocks have language hints

### Agents (`.claude/agents/*.md`)

**Structure validation:**
- [ ] YAML frontmatter has opening and closing `---` delimiters
- [ ] Required field: `name` (lowercase, numbers, hyphens only, max 64 chars)
- [ ] Required field: `description` (max 1024 chars, no XML tags)
- [ ] No examples or XML tags in description field (must be in body)

**Best practices:**
- [ ] Name uses gerund form matching the activity
- [ ] Description explains when the agent should be invoked
- [ ] Body includes concrete examples of appropriate use
- [ ] If agent references skills, those skills exist
- [ ] Clear scope definition (what it handles vs what it doesn't)

### Slash Commands (`.claude/commands/*.md`)

**Structure validation:**
- [ ] YAML frontmatter has `description` field
- [ ] Description is concise (1-2 sentences)

**Best practices:**
- [ ] Uses `$ARGUMENTS` if command accepts input
- [ ] Handles empty `$ARGUMENTS` case (asks user or uses default)
- [ ] Clear step-by-step instructions
- [ ] No ambiguous decision points left to Claude

### CLAUDE.md / Memory Files

**Structure validation:**
- [ ] Valid markdown syntax
- [ ] No broken internal links

**Best practices:**
- [ ] Clear section organization
- [ ] Actionable instructions (not vague guidance)
- [ ] No contradictory rules

### Reference Files (`references/*.md`)

**Validation:**
- [ ] Valid markdown syntax
- [ ] Referenced by parent SKILL.md or agent
- [ ] No orphaned files (exist but never referenced)

### Scripts (`scripts/*.py`, `scripts/*.sh`, etc.)

**Validation:**
- [ ] Valid syntax for language (parse check)
- [ ] Referenced in SKILL.md or agent
- [ ] Has usage documentation (docstring or header comment)
- [ ] Executable permissions if shell script

## Analysis Process

1. **Inventory**: List all tools found in `.claude/`
2. **Validate**: Run all applicable checks for each tool
3. **Categorize findings**:
   - **ERRORS**: Broken functionality (missing required fields, invalid syntax, broken links)
   - **WARNINGS**: Functional but non-conforming to best practices
   - **SUGGESTIONS**: Optimization opportunities
4. **Prioritize**: For each tool, identify top 3 highest-ROI improvements

## Output Format

### Console Summary

Provide a brief summary to the user:

````markdown
## Validation Results

Scanned: X skills, Y agents, Z commands, W other files

### Errors (must fix)
- [tool-name]: description of error

### Warnings (should fix)  
- [tool-name]: description of issue

### Top Improvements
1. [highest impact change]
2. [second highest]
3. [third highest]

Full analysis written to: CLAUDE_MEMO_AI_TOOLS_REVIEW.md
````

### Technical Memo (CLAUDE_MEMO_AI_TOOLS_REVIEW.md)

Create a detailed markdown file with this structure:

````markdown
# Claude AI Tools Review

**Generated:** [timestamp]
**Scope:** [path validated]

## Executive Summary

[2-3 sentence overview of findings]

## Inventory

| Type | Count | With Errors | With Warnings |
|------|-------|-------------|---------------|
| Skills | X | Y | Z |
| Agents | X | Y | Z |
| Commands | X | Y | Z |
| Other | X | Y | Z |

## Detailed Findings

### Skills

#### [skill-name]
**Status:** [PASS | WARNINGS | ERRORS]

**Errors:**
- [list any errors]

**Warnings:**
- [list any warnings]

**Top 3 Improvements:**
1. [improvement + why it matters]
2. [improvement + why it matters]
3. [improvement + why it matters]

[Repeat for each skill]

### Agents

[Same format as skills]

### Commands

[Same format as skills]

## Global Recommendations

[Cross-cutting improvements that affect multiple tools]

## Checklist for Fixes

- [ ] [specific action item]
- [ ] [specific action item]
- [ ] [specific action item]
````

## Validation

After creating the memo, confirm:
1. `CLAUDE_MEMO_AI_TOOLS_REVIEW.md` exists in project root
2. All errors are clearly actionable
3. Summary was provided to user
