"""
File 9: LangFuse via Direct HTTP (Workaround for SDK output bug)
Uses HTTP requests instead of SDK to properly send output to Langfuse
"""

import os
from dotenv import load_dotenv
import time
import json
import requests
import ollama

load_dotenv()

public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
secret_key = os.getenv('LANGFUSE_SECRET_KEY')
base_url = os.getenv('LANGFUSE_BASE_URL', 'https://cloud.langfuse.com')

print(f"[DEBUG] Using base URL: {base_url}")

ollama_client = ollama.Client()


def create_trace_http(trace_name, query, answer, latency_ms):
    """Create a trace using direct HTTP to Langfuse"""

    url = f"{base_url}/api/public/traces"

    payload = {
        "name": trace_name,
        "input": {"query": query},
        "output": {"answer": answer},
        "metadata": {
            "latency_ms": latency_ms,
            "model": "mistral"
        }
    }

    try:
        response = requests.post(
            url,
            json=payload,
            auth=(public_key, secret_key),
            timeout=10
        )

        if response.status_code in [200, 201]:
            trace_id = response.json()['id']
            print(f"✓ Trace created: {trace_id}")
            print(f"View: {base_url}/project/cmshi3anw05jpad0it1pqaib8/traces/{trace_id}\n")
            return trace_id
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error creating trace: {e}")
        return None


def simple_trace_example():
    """Create a simple trace via HTTP"""

    query = "Explain machine learning in simple terms"

    print("--- Simple Trace Example (HTTP) ---\n")

    # Call LLM
    start_time = time.time()

    response = ollama_client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]
    )

    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000
    answer = response['message']['content']

    print(f"✓ LLM response received ({len(answer)} chars)")
    print(f"[DEBUG] Answer: {answer[:60]}...\n")

    # Send to Langfuse via HTTP
    trace_id = create_trace_http("science_qa", query, answer, latency_ms)

    return trace_id


if __name__ == "__main__":
    print("File 9: LangFuse via Direct HTTP")
    print("=" * 60 + "\n")
    print(f"Base URL: {base_url}\n")

    # Verify API keys
    if not public_key or not secret_key:
        print("ERROR: LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY must be set")
        exit(1)

    trace_id = simple_trace_example()

    if trace_id:
        print("\n✓ Trace successfully sent to Langfuse with output!")
        print(f"Check dashboard: {base_url}/project/cmshi3anw05jpad0it1pqaib8/traces/{trace_id}")
    else:
        print("\n✗ Failed to send trace")
