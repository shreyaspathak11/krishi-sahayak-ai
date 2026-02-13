#!/usr/bin/env python3
"""Quick API test"""
import requests
import json

try:
    print("Testing /health...")
    r = requests.get("http://127.0.0.1:8001/health", timeout=10)
    print(f"Status: {r.status_code}")
    
    print("\nTesting /api/chat...")
    payload = {"message": "What is the weather?", "language": "en", "stream": False, "session_id": "test"}
    r = requests.post("http://127.0.0.1:8001/api/chat", json=payload, timeout=30)
    print(f"Status: {r.status_code}")
    resp = r.json()
    print(f"Response: {resp.get('response')}")
    print(f"Tool calls: {len(resp.get('tool_calls', []))}")
    for tc in resp.get('tool_calls', []):
        print(f"  - {tc.get('name')}: {tc.get('status')}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
