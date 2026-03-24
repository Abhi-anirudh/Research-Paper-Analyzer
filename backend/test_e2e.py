import requests
import time
import sys

BASE_URL = "http://localhost:8000/api"

print("1. Uploading dummy.pdf...")
with open("dummy.pdf", "rb") as f:
    response = requests.post(f"{BASE_URL}/upload-paper", files={"file": f})

if response.status_code != 200:
    print(f"Upload failed: {response.status_code} - {response.text}")
    sys.exit(1)

data = response.json()
paper_id = data.get("paper_id")
print(f"   Success! Paper ID: {paper_id}")
print(f"   Indexed {len(data.get('chunks', []))} chunks across {data.get('total_pages')} pages.")

print("\n2. Testing Chat Query...")
query_payload = {
    "paper_id": paper_id,
    "question": "What is the main contribution?"
}
response = requests.post(f"{BASE_URL}/query", json=query_payload)
if response.status_code != 200:
    print(f"Query failed: {response.status_code} - {response.text}")
else:
    print("   Success! Answer:")
    print("   " + response.json().get("answer", "")[:100] + "...")

print("\n3. Testing Summary Generation (Beginner)...")
response = requests.get(f"{BASE_URL}/summary/{paper_id}?level=beginner")
if response.status_code != 200:
    print(f"Summary failed: {response.status_code} - {response.text}")
else:
    print("   Success! Summary:")
    print("   " + response.json().get("summary", "")[:100] + "...")

print("\nEnd-to-End Test Complete!")
