"""Tests for the FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app


client = TestClient(app)


class TestHealthEndpoints:
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Research Paper Analyzer"

    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestUploadEndpoint:
    def test_rejects_non_pdf(self):
        response = client.post(
            "/api/upload-paper",
            files={"file": ("test.txt", b"not a pdf", "text/plain")},
        )
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    def test_rejects_missing_file(self):
        response = client.post("/api/upload-paper")
        assert response.status_code == 422  # Validation error


class TestQueryEndpoint:
    def test_rejects_missing_paper(self):
        response = client.post(
            "/api/query",
            json={"paper_id": "nonexistent", "question": "What is this?"},
        )
        # Should 404 or 500 due to missing index
        assert response.status_code in [404, 500]

    def test_validates_request_body(self):
        response = client.post("/api/query", json={})
        assert response.status_code == 422


class TestSummaryEndpoint:
    def test_rejects_missing_paper(self):
        response = client.get("/api/summary/nonexistent?level=beginner")
        assert response.status_code in [404, 500]

    def test_sections_missing_paper(self):
        response = client.get("/api/summary/nonexistent/sections")
        assert response.status_code == 404
