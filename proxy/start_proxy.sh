#!/bin/bash

# Start LiteLLM Proxy with custom max_tokens handler

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found. Using .env.example as reference."
    echo "Please copy .env.example to .env and configure your API keys."
fi

# Set default max tokens if not set
export MAX_TOKENS_OVERRIDE=${MAX_TOKENS_OVERRIDE:-2048}

echo "Starting LiteLLM Proxy..."
echo "Max tokens override: $MAX_TOKENS_OVERRIDE"

# Start the proxy server
# --config: path to configuration file
# --port: port to run the proxy on (default: 4000)
# --detailed_debug: enable detailed debug logging (optional)

litellm --config proxy_config.yaml --port 4000 --detailed_debug

# Alternative: Run without detailed debug
# litellm --config proxy_config.yaml --port 4000
