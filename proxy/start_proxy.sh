#!/bin/bash

# Start LiteLLM Proxy with custom_max_token handler

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found. Using .env.example as reference."
    echo "Please copy .env.example to .env and configure your API keys."
fi

# Set default custom_max_token if not set
export CUSTOM_MAX_TOKEN_DEFAULT=${CUSTOM_MAX_TOKEN_DEFAULT:-2048}

echo "Starting LiteLLM Proxy..."
echo "Custom max token default: $CUSTOM_MAX_TOKEN_DEFAULT"

# Start the proxy server
# --config: path to configuration file
# --port: port to run the proxy on (default: 4000)
# --detailed_debug: enable detailed debug logging (optional)

litellm --config proxy_config.yaml --port 4000 --detailed_debug

# Alternative: Run without detailed debug
# litellm --config proxy_config.yaml --port 4000
