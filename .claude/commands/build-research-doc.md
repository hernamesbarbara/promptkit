---
description: Convert a directory of interlinked Markdown research files into a single DOCX, preserving structure and links
argument-hint: "[path/to/research-directory] [--output filename.docx]"
allowed-tools: Read, Write, Bash, Glob
---

# /build-research-doc

Convert a research directory containing interlinked Markdown files into a single combined DOCX document.

**Input:** `$ARGUMENTS` — path to the research directory containing:
- A `README.md` with a Table of Contents
- Multiple `.md` files (deep dives) linked from the TOC

**Output:** A DOCX file in the research directory with:
- All content merged in TOC order
- Internal links rewritten as intra-document anchors
- Auto-generated Word TOC via Pandoc

## Prerequisites

- Pandoc must be installed (`brew install pandoc` or equivalent)

## Instructions

1. **Validate input:**
   - If `$ARGUMENTS` is empty, ask the user to provide the research directory path.
   - Verify the directory exists and contains a `README.md`.

2. **Parse README.md Table of Contents:**
   - Find the TOC section (starts with `## Table of Contents` or similar heading containing "Table of Contents").
   - Extract all markdown links `[Title](path.md)` from that section.
   - This determines the canonical order of sections.

3. **Build combined markdown:**
   - Start with the full `README.md` content.
   - For each file referenced in the TOC (in order):
     - Read the file content.
     - If it lacks a top-level `# Heading`, prepend one using the TOC link text.
     - Rewrite internal `.md` links to anchor links:
       - `[Foo](file.md#section)` → `[Foo](#section)`
       - `[Foo](file.md)` → `[Foo](#file)` (using filename stem as anchor)
     - Append with a horizontal rule separator.

4. **Write combined markdown:**
   - Save as `_combined_research.md` in the research directory.

5. **Convert to DOCX:**
   - Run Pandoc with TOC generation:
     ```bash
     pandoc _combined_research.md \
       --from=markdown \
       --to=docx \
       --output=research_project.docx \
       --toc \
       --toc-depth=3
     ```

6. **Report results:**
   - Print the path to the generated DOCX.
   - Optionally note any warnings (missing files, etc.).

## Implementation

The Python script is located at `.claude/commands/scripts/build_research_doc.py` relative to the project root.

**Resolving the script path:**

1. Identify the project root as the directory containing the `.claude/` folder (this is typically where you invoked Claude Code).
2. Build the absolute path to the script:
   ```bash
   SCRIPT_PATH="$(git rev-parse --show-toplevel)/.claude/commands/scripts/build_research_doc.py"
   ```
3. Run the script with the research directory as the argument:
   ```bash
   python3 "$SCRIPT_PATH" "$ARGUMENTS"
   ```

**Alternative (if not in a git repo):**
```bash
SCRIPT_PATH="$PWD/.claude/commands/scripts/build_research_doc.py"
python3 "$SCRIPT_PATH" "$ARGUMENTS"
```

Ensure you are in the project root directory (the one containing `.claude/`) before running the command.

## Error Handling

Handle these error conditions explicitly:

### Pandoc not installed or not found

1. After running the script, check the exit code.
2. If the script fails with a message containing "Pandoc not found" or exit code 1:
   - Tell the user: "Pandoc is required but was not found on your PATH."
   - Provide installation instructions:
     - macOS: `brew install pandoc`
     - Ubuntu/Debian: `sudo apt-get install pandoc`
     - Windows: `choco install pandoc` or download from https://pandoc.org/installing.html
   - Do not attempt to proceed without Pandoc.

### README.md missing or has no Table of Contents

1. If the script fails with "README.md not found":
   - Tell the user: "The research directory must contain a README.md file."
   - Explain: "Create a README.md with a `## Table of Contents` section that links to your markdown files."

2. If the script warns "No markdown file links found in Table of Contents section":
   - Tell the user: "README.md exists but no Table of Contents section was detected."
   - Explain the expected format:
     ```markdown
     ## Table of Contents

     1. [Introduction](part-1-intro.md)
     2. [Analysis](part-2-analysis.md)
     3. [Conclusion](part-3-conclusion.md)
     ```
   - The TOC must use markdown links `[Title](filename.md)` to `.md` files in the same directory.

### Referenced files not found

1. If the script warns about missing files (e.g., "Referenced file not found: part-2.md"):
   - Report each missing file to the user.
   - Suggest: "Check that the file paths in your Table of Contents match the actual filenames in the directory."
   - The script will continue processing other files, but the output may be incomplete.

## Example Usage

```bash
/build-research-doc ~/research/ai-safety-project
/build-research-doc ./docs/quarterly-analysis
```

## Custom Output Filename

By default, the script outputs `research_project.docx` in the research directory. To specify a custom filename, pass the `--output` (or `-o`) flag to the script.

**Default behavior:**
```bash
python3 "$SCRIPT_PATH" "$ARGUMENTS"
# Creates: <research_dir>/research_project.docx
```

**Custom filename:**
```bash
python3 "$SCRIPT_PATH" "$ARGUMENTS" --output final_report.docx
# Creates: <research_dir>/final_report.docx
```

**Short form:**
```bash
python3 "$SCRIPT_PATH" "$ARGUMENTS" -o quarterly_analysis.docx
```

If the user requests a custom output filename when invoking the command, append the `--output` flag to the script invocation. For example, if the user says:

> /build-research-doc ~/research/my-project --output my_custom_report.docx

Run:
```bash
python3 "$SCRIPT_PATH" ~/research/my-project --output my_custom_report.docx
```

The `.docx` extension is optional; the script will add it if missing.

## Link Rewriting Logic

| Original Link | Rewritten Link |
|---------------|----------------|
| `[Foo](part-2.md#details)` | `[Foo](#details)` |
| `[Foo](part-2.md)` | `[Foo](#part-2)` |
| `[External](https://example.com)` | `[External](https://example.com)` (unchanged) |

## Future Extensions

- Google Docs upload via Drive API
- Custom Pandoc reference template for styling
- PDF output option
