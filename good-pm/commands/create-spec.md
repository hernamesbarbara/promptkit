---
description: Create a structured specification document from a name and summary or draft file.
argument-hint: "<name> <summary OR path/to/draft.md>"
---

# Good PM Create Spec

Generate a structured specification document in `.good-pm/specs/`.

## Arguments

Parse `$ARGUMENTS` for two positional arguments:

- `$1` — **name**: Spec name in kebab-case (e.g., `user-auth`, `api-caching`)
- `$2` — **input**: Either a text summary OR a path to a draft `.md` file

---

## Step 1: Validate Prerequisites

Check that Good PM is initialized:

- If `.good-pm/` directory does NOT exist: **Stop and error**
  - Message: "Good PM is not initialized. Run `/good-pm:setup` first."
- If `.good-pm/templates/SPEC_TEMPLATE.md` does NOT exist: **Stop and error**
  - Message: "Missing template. Run `/good-pm:setup --force` to reinstall."

---

## Step 2: Validate Name

Validate `$1` (name) meets requirements:

| Rule | Validation |
|------|------------|
| Required | Must not be empty |
| Format | Lowercase kebab-case only: `a-z`, `0-9`, `-` |
| Length | Maximum 64 characters |
| No leading/trailing hyphens | Must not start or end with `-` |
| No consecutive hyphens | Must not contain `--` |

**Regex pattern:** `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`

If invalid, **stop and error** with specific guidance:
- Empty: "Name is required. Usage: `/good-pm:create-spec <name> <summary>`"
- Invalid format: "Invalid name '{{name}}'. Use lowercase kebab-case (e.g., `user-auth`, `api-v2`)."
- Too long: "Name '{{name}}' exceeds 64 characters."

---

## Step 3: Check for Existing Spec

Check if `.good-pm/specs/SPEC_<name>.md` already exists:

- If exists: **Stop and error**
  - Message: "Spec already exists: `.good-pm/specs/SPEC_<name>.md`. Choose a different name or delete the existing spec."

---

## Step 4: Detect Input Type

Determine if `$2` is a text summary or file path:

**File mode** if ALL of these are true:
- `$2` ends with `.md` (case-insensitive)
- The file exists at that path

**Text summary mode** otherwise.

If `$2` is empty: **Stop and error**
- Message: "Summary or draft file is required. Usage: `/good-pm:create-spec <name> \"<summary>\"` or `/good-pm:create-spec <name> ./draft.md`"

---

## Step 5a: Text Summary Mode

If text summary mode:

1. Validate summary length (max 256 characters)
   - If too long: **Stop and error**
     - Message: "Summary exceeds 256 characters. Use a draft file for longer content: `/good-pm:create-spec <name> ./draft.md`"

2. Read template from `.good-pm/templates/SPEC_TEMPLATE.md`

3. Replace placeholders:
   - `{{NAME}}` → the spec name (from `$1`)
   - `{{SUMMARY}}` → the summary text (from `$2`)
   - `{{DATE}}` → today's date in `YYYY-MM-DD` format

4. Write to `.good-pm/specs/SPEC_<name>.md`

---

## Step 5b: File Mode

If file mode:

1. Read the draft file content from the path in `$2`

2. Analyze the draft content and synthesize a structured spec:
   - Extract or infer a summary from the first paragraph or heading
   - Map draft content to appropriate spec sections
   - Preserve technical details, code examples, and specifics
   - Fill in section headers even if content needs expansion
   - Add placeholder text `[TODO: Fill in this section]` for sections without content

3. Ensure all standard spec sections are present:
   - Overview (from draft intro)
   - Problem Statement (from draft motivation/problem)
   - Goals (extract action items as checkboxes)
   - Non-Goals (if mentioned, otherwise placeholder)
   - Background & Context (any references, prior art)
   - Proposed Solution (main technical content)
   - Implementation Plan (break into phases with checkboxes)
   - Acceptance Criteria (extract or create from goals)
   - Open Questions (any uncertainties from draft)
   - Dependencies (any mentioned requirements)
   - Risks & Mitigations (if mentioned)
   - References (any links from draft)

4. Set metadata:
   - `{{NAME}}` → the spec name (from `$1`)
   - `{{DATE}}` → today's date in `YYYY-MM-DD` format

5. Write to `.good-pm/specs/SPEC_<name>.md`

6. **Delete the original draft file** (it has been synthesized into the spec)

---

## Output

After successful creation, print:

**For text summary mode:**
```
Created spec: .good-pm/specs/SPEC_<name>.md

The spec has been initialized with your summary. Fill in the sections:
  - Overview: Expand on the summary
  - Problem Statement: What problem does this solve?
  - Goals: What must this achieve? (use checkboxes)
  - Proposed Solution: Technical approach
  - Implementation Plan: Break into phases
  - Acceptance Criteria: How do we know it's done?

When ready, break into issues:
  /good-pm:create-issues .good-pm/specs/SPEC_<name>.md
```

**For file mode:**
```
Created spec: .good-pm/specs/SPEC_<name>.md
Deleted draft: <original-path>

The spec has been synthesized from your draft. Review the sections and refine as needed.

When ready, break into issues:
  /good-pm:create-issues .good-pm/specs/SPEC_<name>.md
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Good PM not initialized | Error: "Run `/good-pm:setup` first." |
| Missing template | Error: "Run `/good-pm:setup --force` to reinstall." |
| Empty name | Error with usage hint |
| Invalid name format | Error with kebab-case example |
| Name too long | Error with character count |
| Empty input | Error with usage hint |
| Summary too long | Error suggesting file mode |
| Spec already exists | Error with path to existing spec |
| Draft file not found | Error: "Draft file not found: `<path>`" |
| Cannot write spec | Error: "Failed to write spec. Check permissions." |
| Cannot delete draft | Warning: "Spec created but could not delete draft: `<path>`" |

---

## Examples

```bash
# Text summary mode
/good-pm:create-spec user-auth "OAuth2 authentication with Google and GitHub providers"

# File mode (from existing draft)
/good-pm:create-spec api-caching ./notes/caching-ideas.md

# File mode (from absolute path)
/good-pm:create-spec payment-flow /tmp/payment-draft.md
```
