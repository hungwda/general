#!/usr/bin/env python3
"""
Simple test client for the Pi Agent proxy server
"""
import sys
from openai import OpenAI

def test_proxy(base_url="http://localhost:8000/v1"):
    """Test the proxy server with a simple chat completion"""

    print(f"Testing proxy at {base_url}")
    print("-" * 50)

    client = OpenAI(
        base_url=base_url,
        api_key="dummy-key"  # Not used but required by client
    )

    # Test 1: List models
    print("\n1. Testing /v1/models endpoint...")
    try:
        models = client.models.list()
        print(f"   ✓ Available models: {[m.id for m in models.data]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return

    # Test 2: Non-streaming chat completion
    print("\n2. Testing non-streaming chat completion...")
    try:
        response = client.chat.completions.create(
            model="pi",
            messages=[
                {"role": "user", "content": "Say 'Hello, World!' and nothing else."}
            ],
            max_tokens=50
        )
        print(f"   ✓ Response: {response.choices[0].message.content}")
        print(f"   ✓ Tokens used: {response.usage.total_tokens}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return

    # Test 3: Streaming chat completion
    print("\n3. Testing streaming chat completion...")
    try:
        stream = client.chat.completions.create(
            model="pi",
            messages=[
                {"role": "user", "content": "Count from 1 to 5."}
            ],
            stream=True,
            max_tokens=100
        )
        print("   ✓ Stream response: ", end="")
        for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return

    print("\n" + "-" * 50)
    print("✓ All tests passed!")

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/v1"
    test_proxy(base_url)
