#!/usr/bin/env python3
"""Test the API locally"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing /health ===")
    r = requests.get(f"{BASE_URL}/health")
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

def test_root():
    """Test root endpoint"""
    print("\n=== Testing / ===")
    r = requests.get(f"{BASE_URL}/")
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

def test_chat(message):
    """Test chat endpoint"""
    print(f"\n=== Testing /api/chat with message: '{message}' ===")
    payload = {
        "message": message,
        "language": "en",
        "stream": False,
        "session_id": "test-session"
    }
    r = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"Status: {r.status_code}")
    resp = r.json()
    print(f"Response: {resp.get('response', 'N/A')}")
    print(f"Tool calls: {len(resp.get('tool_calls', []))}")
    if resp.get('tool_calls'):
        for tool in resp['tool_calls']:
            print(f"  - {tool.get('name')}: {tool.get('description')}")
    return resp

if __name__ == "__main__":
    try:
        test_health()
        test_root()
        test_chat("What is the current weather?")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
