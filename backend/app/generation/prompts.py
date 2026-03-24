"""Prompt templates for RAG generation."""

# ── Anti-Hallucination System Prompt ──────────────────────────────

SYSTEM_PROMPT = """You are a precise academic paper analysis assistant.

STRICT RULES:
1. Answer ONLY using the provided context from the paper. Do NOT use any external knowledge.
2. If the answer cannot be found in the provided context, respond EXACTLY: "This information is not found in the paper."
3. Always include section and page references in your answers using the format [Section: X, Page: Y].
4. Be thorough but concise.
5. When explaining equations or formulas, break them down step by step.
6. Maintain academic tone and accuracy."""


# ── Query Template ────────────────────────────────────────────────

QUERY_TEMPLATE = """Based on the following excerpts from a research paper, answer the question.

CONTEXT:
{context}

QUESTION: {question}

Remember: Only use information from the context above. Include [Section, Page] references."""


# ── Summary Templates ─────────────────────────────────────────────

BEGINNER_SUMMARY_TEMPLATE = """Based on the following research paper content, create a beginner-friendly summary.

PAPER CONTENT:
{context}

Instructions:
- Explain as if talking to someone with no background in this field
- Avoid jargon; if you must use technical terms, define them
- Use analogies and simple examples where helpful
- Structure: What problem? → Why it matters? → What did they do? → What did they find?
- Keep it under 500 words
- Include [Section, Page] references"""


TECHNICAL_SUMMARY_TEMPLATE = """Based on the following research paper content, create a detailed technical summary.

PAPER CONTENT:
{context}

Instructions:
- Target audience: researchers and practitioners in the field
- Cover: Problem statement, methodology, key contributions, results, limitations
- Preserve technical details: models, metrics, datasets, hyperparameters
- Note any novel techniques or approaches
- Keep it under 800 words
- Include [Section, Page] references"""


# ── Advanced Feature Templates ────────────────────────────────────

NOVELTY_DETECTION_TEMPLATE = """Based on the following research paper content, identify what makes this paper novel and different.

PAPER CONTENT:
{context}

Analyze:
1. What is the key innovation or novel contribution?
2. How does it differ from existing approaches (if mentioned)?
3. What new techniques, frameworks, or insights does it introduce?
4. What gap in existing research does it address?
Include [Section, Page] references."""


KEY_INSIGHTS_TEMPLATE = """Based on the following research paper content, extract the key insights.

PAPER CONTENT:
{context}

Extract:
1. 3-5 most important findings or takeaways
2. Surprising or counter-intuitive results
3. Practical implications
4. Limitations and future directions acknowledged by the authors
Include [Section, Page] references."""


COMPARISON_TEMPLATE = """Compare the following papers based on their content.

{papers_context}

QUESTION: {question}

Compare across:
1. Research problems addressed
2. Methodologies used
3. Key findings and results
4. Strengths and limitations of each
Include paper identifiers and [Section, Page] references."""


LITERATURE_REVIEW_TEMPLATE = """Based on the following papers, generate a structured literature review.

{papers_context}

Structure the review as:
1. Overview of the research area
2. Common themes and approaches
3. Key differences between papers
4. Research gaps identified
5. Future directions suggested
Include paper identifiers and [Section, Page] references."""
