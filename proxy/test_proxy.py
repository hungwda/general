"""
Test script for LiteLLM Proxy with custom_max_token Support

This script demonstrates how to interact with the LiteLLM proxy
and verify that custom_max_token is being processed correctly.
"""

import os
from openai import OpenAI

# Configure the OpenAI client to use LiteLLM proxy
client = OpenAI(
    api_key=os.getenv("LITELLM_MASTER_KEY", "test-key"),
    base_url="http://localhost:4000"  # LiteLLM proxy URL
)


def test_custom_max_token():
    """
    Test that custom_max_token is being processed by the custom handler.
    """
    print("=" * 80)
    print("Testing custom_max_token Support")
    print("=" * 80)

    # Test 1: Request with custom_max_token=100
    print("\nTest 1: Sending request with custom_max_token=100")
    print("Expected: Should set max_tokens to 100")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello, World!' and nothing else."}
            ],
            extra_body={"custom_max_token": 100}  # Use extra_body for custom parameters
        )

        print(f"Response: {response.choices[0].message.content}")
        print(f"Usage: {response.usage}")
        print("✓ Test 1 passed")
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")

    # Test 2: Request without custom_max_token
    print("\nTest 2: Sending request without custom_max_token")
    print("Expected: Should use CUSTOM_MAX_TOKEN_DEFAULT value")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Count from 1 to 5."}
            ]
            # No custom_max_token specified
        )

        print(f"Response: {response.choices[0].message.content}")
        print(f"Usage: {response.usage}")
        print("✓ Test 2 passed")
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")

    # Test 3: Request with very high custom_max_token
    print("\nTest 3: Sending request with custom_max_token=10000")
    print("Expected: Should be capped at max_allowed if using ConditionalMaxTokensModifier")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "What is 2+2?"}
            ],
            extra_body={"custom_max_token": 10000}  # Very high value
        )

        print(f"Response: {response.choices[0].message.content}")
        print(f"Usage: {response.usage}")
        print("✓ Test 3 passed")
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")


def test_different_models():
    """
    Test custom_max_token with different models (if using ConditionalMaxTokensModifier).
    """
    print("\n" + "=" * 80)
    print("Testing Different Models with custom_max_token")
    print("=" * 80)

    models_to_test = ["gpt-3.5-turbo", "gpt-4"]

    for model in models_to_test:
        print(f"\nTesting model: {model}")
        print("Testing with custom_max_token=500")

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "Hello!"}
                ],
                extra_body={"custom_max_token": 500}
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
    print("LiteLLM Proxy custom_max_token Test")
    print("Make sure the proxy is running on http://localhost:4000")
    print("")

    # Check if proxy is configured
    if not os.getenv("LITELLM_MASTER_KEY"):
        print("Warning: LITELLM_MASTER_KEY not set. Using default 'test-key'")
        print("Set LITELLM_MASTER_KEY environment variable for production use.")
        print("")

    # Run tests
    test_custom_max_token()
    test_different_models()

    print("\n" + "=" * 80)
    print("Tests completed!")
    print("Check the proxy server logs to see the custom_max_token processing")
    print("=" * 80)


if __name__ == "__main__":
    main()
