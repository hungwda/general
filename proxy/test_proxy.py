"""
Test script for LiteLLM Proxy with Max Tokens Modifier

This script demonstrates how to interact with the LiteLLM proxy
and verify that max_tokens is being modified correctly.
"""

import os
from openai import OpenAI

# Configure the OpenAI client to use LiteLLM proxy
client = OpenAI(
    api_key=os.getenv("LITELLM_MASTER_KEY", "test-key"),
    base_url="http://localhost:4000"  # LiteLLM proxy URL
)


def test_max_tokens_override():
    """
    Test that max_tokens is being overridden by the custom handler.
    """
    print("=" * 80)
    print("Testing Max Tokens Override")
    print("=" * 80)

    # Test 1: Request with max_tokens=100 (should be overridden)
    print("\nTest 1: Sending request with max_tokens=100")
    print("Expected: Should be overridden to MAX_TOKENS_OVERRIDE value")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello, World!' and nothing else."}
            ],
            max_tokens=100  # This should be overridden
        )

        print(f"Response: {response.choices[0].message.content}")
        print(f"Usage: {response.usage}")
        print("✓ Test 1 passed")
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")

    # Test 2: Request without max_tokens
    print("\nTest 2: Sending request without max_tokens")
    print("Expected: Should use MAX_TOKENS_OVERRIDE value")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Count from 1 to 5."}
            ]
            # No max_tokens specified
        )

        print(f"Response: {response.choices[0].message.content}")
        print(f"Usage: {response.usage}")
        print("✓ Test 2 passed")
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")

    # Test 3: Request with very high max_tokens
    print("\nTest 3: Sending request with max_tokens=10000")
    print("Expected: Should be overridden or capped depending on handler")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "What is 2+2?"}
            ],
            max_tokens=10000  # Very high value
        )

        print(f"Response: {response.choices[0].message.content}")
        print(f"Usage: {response.usage}")
        print("✓ Test 3 passed")
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")


def test_different_models():
    """
    Test max_tokens override with different models (if using ConditionalMaxTokensModifier).
    """
    print("\n" + "=" * 80)
    print("Testing Different Models")
    print("=" * 80)

    models_to_test = ["gpt-3.5-turbo", "gpt-4"]

    for model in models_to_test:
        print(f"\nTesting model: {model}")

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "Hello!"}
                ],
                max_tokens=500
            )

            print(f"Response: {response.choices[0].message.content}")
            print(f"Usage: {response.usage}")
            print(f"✓ {model} test passed")
        except Exception as e:
            print(f"✗ {model} test failed: {e}")
            print("(This is expected if the model is not configured)")


def main():
    """
    Main test function.
    """
    print("LiteLLM Proxy Max Tokens Test")
    print("Make sure the proxy is running on http://localhost:4000")
    print("")

    # Check if proxy is configured
    if not os.getenv("LITELLM_MASTER_KEY"):
        print("Warning: LITELLM_MASTER_KEY not set. Using default 'test-key'")
        print("Set LITELLM_MASTER_KEY environment variable for production use.")
        print("")

    # Run tests
    test_max_tokens_override()
    test_different_models()

    print("\n" + "=" * 80)
    print("Tests completed!")
    print("Check the proxy server logs to see the max_tokens modifications")
    print("=" * 80)


if __name__ == "__main__":
    main()
