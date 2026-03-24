"""Metadata extractor — pulls title, authors, abstract from parsed sections."""

import re
from app.models.schemas import PaperMetadata, Section


def extract_metadata(
    sections: list[Section],
    paper_id: str,
    filename: str,
    total_pages: int,
) -> PaperMetadata:
    """Extract paper metadata from parsed sections."""
    title = _extract_title(sections)
    authors = _extract_authors(sections)
    abstract = _extract_abstract(sections)
    section_names = [s.title for s in sections]

    return PaperMetadata(
        paper_id=paper_id,
        title=title,
        authors=authors,
        abstract=abstract,
        sections=section_names,
        total_pages=total_pages,
        filename=filename,
    )


def _extract_title(sections: list[Section]) -> str:
    """Extract title — usually the first non-empty text before any section heading."""
    if not sections:
        return "Untitled"

    first = sections[0]
    if first.title == "Preamble" and first.text:
        lines = first.text.strip().split("\n")
        # Title is typically one of the first lines, usually the longest/first
        for line in lines[:3]:
            cleaned = line.strip()
            if len(cleaned) > 10 and not re.match(r"^(https?://|www\.|\d)", cleaned):
                return cleaned
    return first.title if first.title != "Preamble" else "Untitled"


def _extract_authors(sections: list[Section]) -> list[str]:
    """Try to extract authors from the preamble section."""
    if not sections:
        return []

    first = sections[0]
    if first.title != "Preamble":
        return []

    lines = first.text.strip().split("\n")
    authors = []

    for line in lines[1:6]:  # Authors usually in lines 2-5
        line = line.strip()
        # Skip lines that look like affiliations or emails
        if re.search(r"@|university|department|institute|http", line, re.IGNORECASE):
            continue
        # Lines with commas or "and" separating names
        if re.search(r"[A-Z][a-z]+ [A-Z][a-z]+", line):
            if "," in line or " and " in line:
                parts = re.split(r",\s*| and ", line)
                authors.extend([p.strip() for p in parts if p.strip()])
            elif len(line.split()) <= 5:
                authors.append(line)

    return authors[:10]  # Cap at 10


def _extract_abstract(sections: list[Section]) -> str:
    """Find the abstract section."""
    for section in sections:
        if re.match(r"abstract", section.title, re.IGNORECASE):
            return section.text.strip()

    # Sometimes abstract is embedded in preamble
    if sections and sections[0].title == "Preamble":
        text = sections[0].text
        match = re.search(
            r"(?:abstract)[:\.\s]*(.{50,1500}?)(?=\n\s*\n|\n[A-Z])",
            text, re.IGNORECASE | re.DOTALL,
        )
        if match:
            return match.group(1).strip()

    return ""
