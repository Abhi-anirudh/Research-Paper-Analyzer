"""Summary router — generates beginner/technical summaries and section breakdowns."""

import os
import json
from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import SummaryLevel, SummaryResponse, Section
from app.generation.generator import generate_summary
from app.config import get_settings

router = APIRouter(tags=["Summary"])


@router.get("/summary/{paper_id}", response_model=SummaryResponse)
async def get_summary(
    paper_id: str,
    level: SummaryLevel = Query(default=SummaryLevel.BEGINNER),
):
    """Generate a summary of the paper at beginner or technical level."""
    try:
        summary_text, sources = generate_summary(paper_id, level)
        return SummaryResponse(
            paper_id=paper_id,
            level=level,
            summary=summary_text,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Paper '{paper_id}' not found")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{paper_id}/sections", response_model=list[Section])
async def get_sections(paper_id: str):
    """Return the extracted sections of a paper."""
    settings = get_settings()
    meta_path = os.path.join(settings.index_dir, f"{paper_id}.json")

    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail=f"Paper '{paper_id}' not found")

    with open(meta_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # Group chunks by section
    section_map: dict[str, dict] = {}
    for chunk in chunks:
        title = chunk.get("section_title", "Unknown")
        if title not in section_map:
            section_map[title] = {
                "title": title,
                "text_parts": [],
                "pages": set(),
            }
        section_map[title]["text_parts"].append(chunk["text"])
        section_map[title]["pages"].add(chunk.get("page_number", 0))

    sections = []
    for data in section_map.values():
        sections.append(Section(
            title=data["title"],
            text="\n\n".join(data["text_parts"]),
            page_numbers=sorted(data["pages"]),
        ))

    return sections
