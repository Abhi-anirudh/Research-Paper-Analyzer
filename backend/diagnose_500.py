import httpx
import json

try:
    # Use the paper_id from the last successful upload in test_e2e.py
    # If not sure, we can list uploads
    response = httpx.get("http://localhost:8000/api/summary/b9e3e?level=beginner", timeout=60.0)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
