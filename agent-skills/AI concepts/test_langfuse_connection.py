#!/usr/bin/env python3
"""Test if Langfuse connection actually works"""

import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
secret_key = os.getenv("LANGFUSE_SECRET_KEY")
baseurl = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
# Ensure it has https://
if baseurl and not baseurl.startswith("http"):
    baseurl = f"https://{baseurl}"

print(f"Testing Langfuse Connection")
print(f"=" * 60)
print(f"Public Key: {public_key[:15]}...")
print(f"Secret Key: {secret_key[:15]}...")
print(f"Base URL: {baseurl}")
print()

# Test direct HTTP request to Langfuse
url = f"{baseurl}/api/public/traces"

headers = {
    "Content-Type": "application/json",
}

auth = (public_key, secret_key)

# Create a simple trace payload
payload = {
    "name": "test_trace",
    "input": {"query": "test"},
    "output": {"answer": "test"},
    "userId": "test_user"
}

print(f"Sending POST to: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()

try:
    response = requests.post(url, json=payload, auth=auth, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200 or response.status_code == 201:
        print("\n✓ Connection successful!")
    else:
        print("\n✗ Connection failed!")

except Exception as e:
    print(f"✗ Error: {e}")
