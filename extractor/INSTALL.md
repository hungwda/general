# Installation Guide

Step-by-step installation guide for Medical Data Extractor.

## Prerequisites

- Python 3.8 or higher
- 8GB RAM minimum (16GB recommended for larger models)
- 10GB free disk space for models
- Internet connection for initial setup

## Installation Steps

### Option 1: Quick Start (Recommended)

Run the automated setup script:

```bash
cd extractor
chmod +x quick_start.sh
./quick_start.sh
```

This will:
1. Check if Ollama is installed
2. Start Ollama if not running
3. Install the LLaVA vision model
4. Install Python dependencies

### Option 2: Manual Installation

#### Step 1: Install Ollama

Choose your platform:

##### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

##### macOS
```bash
brew install ollama
```

##### Windows
Download and install from [ollama.ai](https://ollama.ai)

#### Step 2: Start Ollama

```bash
ollama serve
```

Keep this running in a separate terminal.

#### Step 3: Install Vision Model

In a new terminal:

```bash
# Standard model (7B parameters, ~4GB)
ollama pull llava:latest

# Optional: Larger models for better accuracy
ollama pull llava:13b  # ~8GB
ollama pull llava:34b  # ~20GB
```

#### Step 4: Install Python Dependencies

```bash
cd extractor
pip install -r requirements.txt
```

Or install in a virtual environment:

```bash
cd extractor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Verify Installation

Run the test script:

```bash
python test_installation.py
```

This will check:
- Python version
- Required packages
- Ollama connection
- Available models
- Module imports

Expected output:
```
✓ Python 3.x.x
✓ All packages installed
✓ Connected to Ollama
✓ Vision models available
✓ All tests passed!
```

## First Run

Try extracting from a sample document:

```bash
python main.py --file /path/to/sample_medical_report.pdf
```

The extracted data will be saved in the `output/` directory.

## Troubleshooting

### Ollama Not Found

If you get "Ollama is not installed":
1. Install Ollama using instructions above
2. Verify with: `ollama --version`
3. Make sure it's in your PATH

### Ollama Connection Error

If you get "Cannot connect to Ollama":
1. Start Ollama: `ollama serve`
2. Check if running: `curl http://localhost:11434/api/tags`
3. Check firewall settings

### Model Not Found

If you get "Model not found":
1. List installed models: `ollama list`
2. Install required model: `ollama pull llava:latest`
3. Wait for download to complete

### Python Package Errors

If you get import errors:
1. Verify Python version: `python --version` (must be 3.8+)
2. Reinstall packages: `pip install -r requirements.txt --force-reinstall`
3. Try using a virtual environment

### Memory Issues

If you get out-of-memory errors:
1. Use smaller model: `--model llava:latest` instead of llava:13b
2. Reduce DPI: `--dpi 150`
3. Process files one at a time instead of batch
4. Close other applications

### PDF Processing Errors

If PDFs fail to process:
1. Check if PDF is valid: Open in a PDF reader
2. Ensure PDF is not encrypted or password-protected
3. Try converting PDF to images first
4. Check if PyMuPDF is installed: `pip install pymupdf`

## Platform-Specific Notes

### Linux

May need to install additional dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev python3-pip

# Fedora/RHEL
sudo dnf install python3-devel python3-pip
```

### macOS

If you get SSL errors:

```bash
# Install certificates
/Applications/Python\ 3.x/Install\ Certificates.command
```

### Windows

1. Run Command Prompt or PowerShell as Administrator
2. If you get execution policy errors:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

## Upgrading

To upgrade to a newer version:

```bash
# Update Python packages
pip install -r requirements.txt --upgrade

# Update Ollama models
ollama pull llava:latest
```

## Uninstallation

To remove the Medical Data Extractor:

```bash
# Remove Python packages
pip uninstall -r requirements.txt -y

# Remove Ollama models (optional)
ollama rm llava:latest

# Uninstall Ollama (optional)
# Linux/macOS: Remove via package manager
# Windows: Use Add/Remove Programs
```

## Next Steps

After successful installation:

1. Read the README.md for usage instructions
2. Check example_usage.py for code examples
3. Try processing a sample document
4. Review config.py for customization options

## Getting Help

If you encounter issues not covered here:

1. Run the test script: `python test_installation.py`
2. Check the README.md troubleshooting section
3. Verify Ollama is running and models are downloaded
4. Check system requirements are met

## System Requirements Summary

| Component | Minimum | Recommended |
| --------- | ------- | ----------- |
| Python    | 3.8     | 3.10+       |
| RAM       | 8GB     | 16GB        |
| Disk Space| 5GB     | 20GB        |
| CPU       | 4 cores | 8+ cores    |
| GPU       | None    | NVIDIA GPU  |

Note: GPU is optional but will significantly speed up processing if available.
