"""FastAPI application entry point — Research Paper Analyzer."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import upload, query, summary

app = FastAPI(
    title="Research Paper Analyzer",
    description=(
        "RAG-based API for uploading academic papers and interacting with them "
        "through conversational AI. Features anti-hallucination mode, "
        "citation-aware answers, and multi-document comparison."
    ),
    version="1.0.0",
)

# CORS — allow Angular dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(upload.router, prefix="/api")
app.include_router(query.router, prefix="/api")
app.include_router(summary.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "service": "Research Paper Analyzer",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
