#!/bin/bash

# Medical Data Extractor - Quick Start Script

echo "========================================"
echo "Medical Data Extractor - Quick Start"
echo "========================================"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null
then
    echo "ERROR: Ollama is not installed!"
    echo ""
    echo "Please install Ollama first:"
    echo "  Linux:   curl -fsSL https://ollama.ai/install.sh | sh"
    echo "  macOS:   brew install ollama"
    echo "  Windows: Download from ollama.ai"
    echo ""
    exit 1
fi

echo "✓ Ollama is installed"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags &> /dev/null
then
    echo "⚠ Ollama is not running. Starting Ollama..."
    ollama serve &
    sleep 3
fi

echo "✓ Ollama is running"

# Check if llava model is installed
if ! ollama list | grep -q "llava"
then
    echo ""
    echo "Installing LLaVA vision model (this may take a few minutes)..."
    ollama pull llava:latest
    echo "✓ LLaVA model installed"
else
    echo "✓ LLaVA model is already installed"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "You can now use the Medical Data Extractor:"
echo ""
echo "  Single file:    python main.py --file path/to/report.pdf"
echo "  Directory:      python main.py --directory path/to/records"
echo "  Help:           python main.py --help"
echo ""
echo "See README.md for more usage examples."
echo ""
