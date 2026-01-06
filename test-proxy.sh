#!/bin/bash
# Test script for mock LiteLLM proxy server

echo "=========================================="
echo "Mock LiteLLM Proxy - Test Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8000"

echo -e "${BLUE}1. Testing Health Endpoint${NC}"
echo "---"
curl -s "${BASE_URL}/health" | jq .
echo ""
echo ""

echo -e "${BLUE}2. Testing Non-Streaming Mode${NC}"
echo "---"
curl -s "${BASE_URL}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-test-key" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "stream": false
  }' | jq .
echo ""
echo ""

echo -e "${BLUE}3. Testing Streaming Mode${NC}"
echo "---"
curl -s "${BASE_URL}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-test-key" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Tell me something interesting"}
    ],
    "stream": true,
    "stream_options": {"include_usage": true}
  }'
echo ""
echo ""

echo -e "${GREEN}✓ All tests completed${NC}"
