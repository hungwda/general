"""
Configuration settings for Medical Data Extractor.
"""

from pathlib import Path


class Config:
    """Configuration settings."""

    # Model settings
    DEFAULT_MODEL = "llava:latest"
    ALTERNATIVE_MODELS = ["llava:7b", "llava:13b", "llava:34b"]

    # Processing settings
    DEFAULT_DPI = 200
    HIGH_QUALITY_DPI = 300
    FAST_DPI = 150

    # Output settings
    DEFAULT_OUTPUT_DIR = "output"

    # Supported file formats
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    SUPPORTED_PDF_FORMAT = '.pdf'

    # Ollama settings
    DEFAULT_OLLAMA_HOST = None  # Uses default local
    OLLAMA_TIMEOUT = 300  # seconds

    # Extraction settings
    COMBINE_PAGES = True
    CREATE_INDEX = True
    CREATE_SUMMARY = True

    # PII Redaction settings
    ENABLE_REDACTION = True
    REDACTION_MARKER = "[REDACTED]"
    REDACTION_TYPES = {
        'names',        # Person names
        'dob',          # Dates of birth
        'ids',          # Patient IDs, MRNs, SSNs, etc.
        'contact',      # Phone, email, addresses
        'age_over_89'   # Ages over 89 (HIPAA requirement)
    }

    # System prompt for extraction
    SYSTEM_PROMPT = """You are a medical data extraction assistant. Your task is to extract all relevant medical information from documents and format them in clean markdown.

IMPORTANT FORMATTING RULES:
- Use plain markdown with NO bold (**) or italic (*) text
- Use headers (#, ##, ###) to organize sections
- Use tables for structured data
- Use lists (-, 1., 2.) for multiple items
- Preserve all medical data including patient information, diagnoses, medications, lab results, etc.
- Maintain accuracy - do not interpret or change medical terminology
- If text is unclear or illegible, note it as [unclear] or [illegible]

Extract and organize information into relevant sections such as:
- Patient Information
- Medical History
- Current Medications
- Diagnosis
- Laboratory Results
- Treatment Plan
- Physician Notes

Format tables properly using markdown table syntax:

| Header 1 | Header 2 | Header 3 |
| -------- | -------- | -------- |
| Data 1   | Data 2   | Data 3   |
"""

    # User prompt templates
    DEFAULT_USER_PROMPT = "Extract all medical information from this document and format it in clean markdown. Do not use bold or italic formatting. Use tables where appropriate."

    LAB_RESULTS_PROMPT = "Extract all laboratory test results including test names, values, units, and reference ranges. Format as a clear markdown table."

    PATIENT_DEMOGRAPHICS_PROMPT = "Extract patient demographic information including name, ID, date of birth, contact information, and insurance details."

    MEDICATIONS_PROMPT = "Extract all medications including drug names, dosages, frequencies, routes of administration, and prescriber information."

    DIAGNOSIS_PROMPT = "Extract all diagnoses (primary and secondary), ICD codes if present, and related clinical notes."

    COMPREHENSIVE_PROMPT = """Perform a comprehensive extraction of all medical information from this document.
Include all details such as:
- Complete patient demographics
- Full medical history
- All laboratory results with units and reference ranges
- Complete medication list with dosages
- All diagnoses (primary and secondary)
- Treatment plans and recommendations
- Physician notes and observations

Organize information clearly using headers and tables where appropriate.
Maintain medical accuracy - do not interpret or modify any values.
Use plain markdown with no bold or italic formatting.
"""

    @classmethod
    def get_model_list(cls):
        """Get list of recommended models."""
        return [cls.DEFAULT_MODEL] + cls.ALTERNATIVE_MODELS

    @classmethod
    def get_supported_formats(cls):
        """Get list of all supported file formats."""
        return cls.SUPPORTED_IMAGE_FORMATS + [cls.SUPPORTED_PDF_FORMAT]

    @classmethod
    def validate_file_format(cls, file_path: Path) -> bool:
        """Check if file format is supported."""
        suffix = file_path.suffix.lower()
        return suffix in cls.get_supported_formats()
