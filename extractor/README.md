# Medical Data Extractor

A privacy-first, local pipeline for extracting medical data from 100+ documents in PDF and image formats. Uses Ollama vision models for accurate structured extraction with output in clean markdown format.

## Features

- Process PDFs and images (JPG, PNG, BMP, TIFF)
- Local processing using Ollama vision models
- Privacy-first: No data sent to external APIs
- Structured markdown output with no bold/italic formatting
- Support for tables and organized data
- Batch processing of multiple documents
- Automatic page handling for multi-page PDFs
- Progress tracking and error reporting
- Index and summary generation for batch jobs

## Requirements

- Python 3.8+
- Ollama installed and running locally
- A vision model installed in Ollama (llava recommended)

## Installation

### Step 1: Install Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai)

For Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

For macOS:
```bash
brew install ollama
```

For Windows:
Download installer from ollama.ai

### Step 2: Install Vision Model

Install the llava vision model (recommended for medical documents):

```bash
# Standard model (faster)
ollama pull llava:latest

# Or larger model for better accuracy
ollama pull llava:13b
ollama pull llava:34b
```

### Step 3: Install Python Dependencies

```bash
cd extractor
pip install -r requirements.txt
```

## Quick Start

### Process a Single File

```bash
python main.py --file path/to/medical_report.pdf
```

### Process All Files in a Directory

```bash
python main.py --directory path/to/medical_records
```

### Use a Specific Model

```bash
python main.py --file report.pdf --model llava:13b
```

### Custom Output Directory

```bash
python main.py --directory ./records --output ./extracted_data
```

## Usage

### Command Line Interface

```bash
python main.py [OPTIONS]

Options:
  -f, --file FILE              Process a single file
  -d, --directory DIR          Process all files in directory
  -m, --model MODEL            Ollama model to use (default: llava:latest)
  -o, --output DIR             Output directory (default: output)
  --output-filename NAME       Custom filename for single file
  --dpi DPI                    DPI for PDF conversion (default: 200)
  --prompt TEXT                Custom extraction prompt
  --no-index                   Skip index file creation
  --no-summary                Skip summary file creation
  --ollama-host URL           Custom Ollama host URL
```

### Python API

```python
from pipeline import MedicalDataExtractor

# Initialize extractor
extractor = MedicalDataExtractor(
    model="llava:latest",
    output_dir="output",
    dpi=200
)

# Extract from single file
result = extractor.extract_from_file(
    file_path="medical_report.pdf",
    save_output=True
)

# Extract from directory
result = extractor.extract_from_directory(
    directory="medical_records",
    create_index=True,
    create_summary=True
)

# Extract from file list
result = extractor.extract_from_file_list(
    file_paths=["report1.pdf", "report2.pdf"],
    create_index=True
)
```

### Custom Extraction Prompts

```python
custom_prompt = """
Extract only patient demographics and primary diagnosis.
Format as markdown with clear sections.
Do not use bold or italic formatting.
"""

result = extractor.extract_from_file(
    file_path="report.pdf",
    custom_prompt=custom_prompt
)
```

## Output Format

All extracted data is saved in markdown format with:

- Metadata header (source file, extraction date)
- Structured sections with headers
- Tables for structured data
- Plain text (no bold or italic)
- Lists for multiple items

Example output:

```markdown
<!--
Extraction Metadata:
- Source File: medical_report.pdf
- Extraction Date: 2024-01-15 10:30:00
-->

# Medical Document

## Patient Information

- Name: John Doe
- ID: 12345
- Date of Birth: 1980-05-15

## Laboratory Results

| Test Name | Result | Unit | Reference Range |
| --------- | ------ | ---- | --------------- |
| Glucose   | 95     | mg/dL| 70-100          |
| Hemoglobin| 14.5   | g/dL | 13.5-17.5       |

## Diagnosis

Primary: Type 2 Diabetes Mellitus
Secondary: Hypertension
```

## Privacy and Security

This tool is designed with privacy as a priority:

- All processing happens locally on your machine
- No data is sent to external APIs or cloud services
- Uses local Ollama models running on your hardware
- No internet connection required after model download
- All extracted data stays on your local filesystem
- HIPAA-compliant when used in appropriate environment

## Performance Tips

### Model Selection

- `llava:latest` (7B): Fast, good for most documents
- `llava:13b`: Better accuracy, moderate speed
- `llava:34b`: Best accuracy, slower processing

### DPI Settings

- 150 DPI: Faster processing, may miss small text
- 200 DPI: Balanced (recommended)
- 300 DPI: Better quality, slower processing

### Batch Processing

For large batches (100+ files):

```bash
python main.py --directory ./records --dpi 150 --model llava:latest
```

## Project Structure

```
extractor/
├── main.py                 # CLI entry point
├── pipeline.py            # Main extraction pipeline
├── document_processor.py  # PDF/image processing
├── llm_extractor.py       # LLM-based extraction
├── output_handler.py      # Output file management
├── example_usage.py       # Usage examples
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve
```

### Model Not Found

```bash
# List installed models
ollama list

# Install required model
ollama pull llava:latest
```

### Memory Issues

If processing large PDFs causes memory issues:

- Reduce DPI: `--dpi 150`
- Use smaller model: `--model llava:latest`
- Process files individually instead of batch

### Poor Extraction Quality

- Increase DPI: `--dpi 300`
- Use larger model: `--model llava:13b`
- Ensure source documents are high quality
- Try custom prompts for specific data types

## Advanced Usage

### Custom Model Configuration

```python
from pipeline import MedicalDataExtractor

# Use custom Ollama host
extractor = MedicalDataExtractor(
    model="llava:13b",
    ollama_host="http://localhost:11434"
)
```

### Processing Specific Document Types

```python
# For lab reports
lab_prompt = "Extract all laboratory test results with values, units, and reference ranges."

# For prescriptions
rx_prompt = "Extract patient info, all medications with dosages, and prescriber details."

# For radiology reports
rad_prompt = "Extract findings, impressions, and recommendations from this radiology report."
```

## Examples

See `example_usage.py` for comprehensive examples including:

- Single file extraction
- Batch directory processing
- Custom prompts
- File list processing
- Model comparison
- High-quality extraction

## License

This project is provided as-is for medical data extraction purposes. Ensure compliance with HIPAA and local privacy regulations when processing medical data.

## Contributing

Contributions welcome! Please ensure all PRs maintain privacy-first principles and local processing.

## Support

For issues and questions:
- Check troubleshooting section
- Review example usage
- Ensure Ollama is properly configured
- Verify vision model is installed

## Acknowledgments

- Ollama for local LLM infrastructure
- PyMuPDF for PDF processing
- LLaVA model for vision capabilities
