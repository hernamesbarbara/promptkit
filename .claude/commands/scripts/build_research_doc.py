#!/usr/bin/env python3
"""
Build a single combined Markdown file from a research directory, then
convert it to DOCX via Pandoc, preserving headings and links.

Usage:
    python build_research_doc.py /path/to/research_dir
    python build_research_doc.py /path/to/research_dir --output custom_name.docx
    python build_research_doc.py /path/to/research_dir -o my_report.docx

Arguments:
    research_dir    Path to the research directory (required)

Options:
    --output, -o    Custom output DOCX filename (default: research_project.docx)
                    The file is created in the research directory.

The research directory must contain:
- README.md with a Table of Contents section
- Markdown files referenced in the TOC

Output:
- _combined_research.md (intermediate combined markdown)
- <output>.docx (final Word document, default: research_project.docx)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def find_toc_links(readme_text: str) -> list[tuple[str, str]]:
    """
    Extract (link_text, link_target) pairs from the Table of Contents section.

    Looks for a heading containing "Table of Contents" and extracts all markdown
    links until the next heading of equal or higher level.

    Returns an ordered list of (title, relative_path) tuples.
    """
    lines = readme_text.splitlines()
    toc_started = False
    toc_heading_level = 0
    toc_lines: list[str] = []

    for line in lines:
        if not toc_started:
            # Look for any heading containing "Table of Contents"
            heading_match = re.match(r"^(#{1,6})\s+.*Table of Contents", line, re.IGNORECASE)
            if heading_match:
                toc_started = True
                toc_heading_level = len(heading_match.group(1))
            continue

        # Stop when we hit a heading of equal or higher level
        heading_match = re.match(r"^(#{1,6})\s+", line)
        if heading_match:
            level = len(heading_match.group(1))
            if level <= toc_heading_level:
                break

        toc_lines.append(line)

    toc_text = "\n".join(toc_lines)

    # Extract markdown links: [Title](target)
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    links: list[tuple[str, str]] = []

    for title, target in pattern.findall(toc_text):
        # Only include links to .md files (not anchors or external URLs)
        if target.endswith(".md") or ".md#" in target:
            # Strip any fragment for the file path
            file_path = target.split("#")[0] if "#" in target else target
            if file_path:  # Don't add empty paths (pure anchors)
                links.append((title, file_path))

    return links


def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug for anchor links.

    Matches common markdown heading ID generation:
    - Lowercase
    - Replace spaces with hyphens
    - Remove non-alphanumeric characters (except hyphens)
    """
    slug = text.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def get_first_heading(markdown_text: str) -> str | None:
    """
    Extract the first top-level heading from markdown text.

    Returns the heading text (without the # prefix) or None if not found.
    """
    match = re.search(r"^#\s+(.+)$", markdown_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def build_heading_map(root_dir: Path, toc_links: list[tuple[str, str]]) -> dict[str, str]:
    """
    Build a mapping from filename stems to their first heading slugs.

    This allows more accurate link rewriting when files have headings
    that don't match their filenames.
    """
    heading_map: dict[str, str] = {}

    for _, rel_path in toc_links:
        md_path = (root_dir / rel_path).resolve()
        if md_path.exists():
            content = md_path.read_text(encoding="utf-8")
            heading = get_first_heading(content)
            stem = Path(rel_path).stem
            if heading:
                heading_map[stem] = slugify(heading)
            else:
                heading_map[stem] = stem

    return heading_map


def rewrite_internal_links(markdown_text: str, heading_map: dict[str, str] | None = None) -> str:
    """
    Rewrite links pointing to .md files as intra-document anchor links.

    Examples:
        [Foo](part-2-foo.md#details) -> [Foo](#details)
        [Foo](part-2-foo.md)         -> [Foo](#part-2-foo) or [Foo](#first-heading-slug)

    Args:
        markdown_text: The markdown content to process.
        heading_map: Optional mapping from filename stems to heading slugs.
    """
    if heading_map is None:
        heading_map = {}

    def replacement(match: re.Match) -> str:
        text = match.group(1)
        target = match.group(2)

        # Leave external URLs alone
        if target.startswith(("http://", "https://", "mailto:")):
            return match.group(0)

        # Only process .md links
        if ".md" not in target:
            return match.group(0)

        # Handle fragment links
        if "#" in target:
            file_part, frag = target.split("#", 1)
            if file_part:
                # Link to another file's section
                return f"[{text}](#{frag})"
            else:
                # Already an anchor link
                return match.group(0)
        else:
            # Link to another file without fragment
            stem = Path(target).stem
            # Use heading map if available, otherwise use filename stem
            anchor = heading_map.get(stem, stem)
            return f"[{text}](#{anchor})"

    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    return pattern.sub(replacement, markdown_text)


def build_combined_markdown(root_dir: Path, output_path: Path) -> list[str]:
    """
    Build a single combined markdown file from the research directory.

    Process:
    1. Read README.md and extract TOC links
    2. Include README.md content at the top
    3. Append each section file in TOC order
    4. Rewrite internal links to anchors
    5. Write combined content to output_path

    Returns a list of warning messages for any issues encountered.
    """
    warnings: list[str] = []

    readme_path = root_dir / "README.md"
    if not readme_path.exists():
        raise FileNotFoundError(f"README.md not found at {readme_path}")

    readme_text = readme_path.read_text(encoding="utf-8")
    toc_links = find_toc_links(readme_text)

    if not toc_links:
        warnings.append("No markdown file links found in Table of Contents section")

    # Build heading map for accurate link rewriting
    heading_map = build_heading_map(root_dir, toc_links)

    parts: list[str] = []

    # Add README as intro (with links rewritten)
    readme_rewritten = rewrite_internal_links(readme_text, heading_map)
    parts.append(readme_rewritten)
    parts.append("\n\n---\n\n")

    # Track which files we've already included (to avoid duplicates)
    included_files: set[str] = {str(readme_path.resolve())}

    # Add each deep-dive file in TOC order
    for title, rel_path in toc_links:
        md_path = (root_dir / rel_path).resolve()

        if str(md_path) in included_files:
            continue

        if not md_path.exists():
            warnings.append(f"Referenced file not found: {rel_path}")
            continue

        included_files.add(str(md_path))
        section_text = md_path.read_text(encoding="utf-8")

        # Check if file has a top-level heading
        existing_heading = get_first_heading(section_text)
        if not existing_heading:
            # Prepend a heading using the TOC title
            section_header = f"# {title}\n\n"
            section_text = section_header + section_text

        # Rewrite internal links
        section_text = rewrite_internal_links(section_text, heading_map)

        parts.append(section_text)
        parts.append("\n\n---\n\n")

    combined = "\n".join(parts)

    # Final pass to catch any remaining internal links
    combined = rewrite_internal_links(combined, heading_map)

    output_path.write_text(combined, encoding="utf-8")
    return warnings


def convert_to_docx(markdown_path: Path, docx_path: Path, toc_depth: int = 3) -> None:
    """
    Convert the combined markdown file to DOCX using Pandoc.

    Includes automatic table of contents generation.

    Args:
        markdown_path: Path to the combined markdown file.
        docx_path: Path for the output DOCX file.
        toc_depth: Maximum heading depth to include in TOC (default: 3).
    """
    cmd = [
        "pandoc",
        str(markdown_path),
        "--from=markdown",
        "--to=docx",
        "--output",
        str(docx_path),
        "--toc",
        f"--toc-depth={toc_depth}",
    ]

    print(f"Running: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Pandoc error: {e.stderr}", file=sys.stderr)
        raise
    except FileNotFoundError:
        print(
            "Error: Pandoc not found. Install it with 'brew install pandoc' or equivalent.",
            file=sys.stderr,
        )
        raise


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert a research directory of Markdown files to a single DOCX.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s ~/research/my-project
    %(prog)s ~/research/my-project --output final_report.docx
    %(prog)s ./docs -o quarterly_analysis.docx
        """,
    )
    parser.add_argument(
        "research_dir",
        type=Path,
        help="Path to the research directory containing README.md and markdown files",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="research_project.docx",
        help="Output DOCX filename (default: research_project.docx)",
    )
    return parser.parse_args()


def main() -> int:
    """
    Entry point: parses arguments and runs the conversion.

    Returns 0 on success, 1 on error.
    """
    args = parse_args()

    root_dir = args.research_dir.expanduser().resolve()

    if not root_dir.is_dir():
        print(f"Error: Not a directory: {root_dir}", file=sys.stderr)
        return 1

    combined_md = root_dir / "_combined_research.md"

    # Ensure output filename ends with .docx
    output_filename = args.output
    if not output_filename.endswith(".docx"):
        output_filename += ".docx"

    output_docx = root_dir / output_filename

    print(f"Processing research directory: {root_dir}")

    try:
        warnings = build_combined_markdown(root_dir, combined_md)
        print(f"Created combined markdown: {combined_md}")

        for warning in warnings:
            print(f"Warning: {warning}", file=sys.stderr)

        convert_to_docx(combined_md, output_docx)
        print(f"Created DOCX: {output_docx}")

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError:
        print("Error: Pandoc conversion failed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
