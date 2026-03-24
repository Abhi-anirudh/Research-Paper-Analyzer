"""PDF parser using PyMuPDF — extracts text, detects sections, and captures page-level data."""

import fitz  # PyMuPDF
import re
from app.models.schemas import Section


def extract_text_by_page(pdf_path: str) -> list[dict]:
    """Extract text from each page of the PDF with font metadata."""
    doc = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        page_data = {"page_number": page_num, "blocks": [], "raw_text": page.get_text()}

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                line_text = ""
                max_font_size = 0
                is_bold = False

                for span in line["spans"]:
                    line_text += span["text"]
                    max_font_size = max(max_font_size, span["size"])
                    if "bold" in span["font"].lower() or "Bold" in span["font"]:
                        is_bold = True

                line_text = line_text.strip()
                if line_text:
                    page_data["blocks"].append({
                        "text": line_text,
                        "font_size": max_font_size,
                        "is_bold": is_bold,
                    })

        pages.append(page_data)

    doc.close()
    return pages


def _is_heading(block: dict, avg_font_size: float) -> bool:
    """Heuristic: a line is a heading if it's bold or has noticeably larger font."""
    if block["is_bold"] and block["font_size"] >= avg_font_size:
        return True
    if block["font_size"] > avg_font_size * 1.15:
        return True
    # Common section heading patterns
    text = block["text"].strip()
    if re.match(
        r"^(\d+\.?\s+)?(Abstract|Introduction|Related Work|Methodology|"
        r"Methods|Results|Discussion|Conclusion|References|Acknowledgments|"
        r"Experiments|Evaluation|Background|Limitations|Future Work|Appendix)",
        text, re.IGNORECASE,
    ):
        return True
    return False


def detect_sections(pages: list[dict]) -> list[Section]:
    """Detect sections from parsed page data using heading heuristics."""
    # Calculate average font size across the document
    all_sizes = []
    for page in pages:
        for block in page["blocks"]:
            all_sizes.append(block["font_size"])

    if not all_sizes:
        # Fallback: treat entire document as one section
        full_text = "\n".join(p["raw_text"] for p in pages)
        return [Section(
            title="Full Document",
            text=full_text,
            page_numbers=list(range(1, len(pages) + 1)),
        )]

    avg_font_size = sum(all_sizes) / len(all_sizes)

    sections: list[Section] = []
    current_title = "Preamble"
    current_text_parts: list[str] = []
    current_pages: set[int] = set()

    for page in pages:
        for block in page["blocks"]:
            if _is_heading(block, avg_font_size) and len(block["text"].split()) <= 12:
                # Save previous section
                if current_text_parts:
                    sections.append(Section(
                        title=current_title,
                        text="\n".join(current_text_parts).strip(),
                        page_numbers=sorted(current_pages),
                    ))
                current_title = block["text"].strip()
                current_text_parts = []
                current_pages = {page["page_number"]}
            else:
                current_text_parts.append(block["text"])
                current_pages.add(page["page_number"])

    # Final section
    if current_text_parts:
        sections.append(Section(
            title=current_title,
            text="\n".join(current_text_parts).strip(),
            page_numbers=sorted(current_pages),
        ))

    return sections


def parse_pdf(pdf_path: str) -> list[Section]:
    """Main entry point: parse PDF and return structured sections."""
    pages = extract_text_by_page(pdf_path)
    return detect_sections(pages)
