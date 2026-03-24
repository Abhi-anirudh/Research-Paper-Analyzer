# Research Paper Analyzer

A full-stack RAG-based system for uploading academic PDFs and interacting with them through citation-aware, anti-hallucination conversational AI.

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────┐
│   Angular    │────▶│              FastAPI Backend              │
│   Frontend   │◀────│                                          │
│              │     │  ┌──────────┐ ┌───────────┐ ┌─────────┐ │
│  • Chat UI   │     │  │Ingestion │ │ Retrieval │ │Generate │ │
│  • Upload    │     │  │          │ │           │ │         │ │
│  • Sections  │     │  │PyMuPDF   │ │ FAISS     │ │ Gemini  │ │
│  • Summary   │     │  │Chunker   │ │ S-Trans   │ │ Prompts │ │
│              │     │  └──────────┘ └───────────┘ └─────────┘ │
└─────────────┘     └──────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Google Gemini API key

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Add your GEMINI_API_KEY
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npx ng serve
```

### Docker
```bash
GEMINI_API_KEY=your-key docker-compose up --build
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload-paper` | POST | Upload PDF, runs full ingestion pipeline |
| `/api/query` | POST | Ask a question (RAG answer + sources) |
| `/api/query/novelty` | POST | Detect paper novelty |
| `/api/query/insights` | POST | Extract key insights |
| `/api/summary/{id}` | GET | Auto-summary (beginner/technical) |
| `/api/summary/{id}/sections` | GET | Section breakdown |
| `/api/compare` | POST | Multi-paper comparison |
| `/api/literature-review` | POST | Generate literature review |

## 🧪 Testing
```bash
cd backend
pytest tests/ -v
```

## 📄 License
MIT
