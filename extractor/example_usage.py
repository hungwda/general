#!/usr/bin/env python3
"""
Example usage of the Medical Data Extractor pipeline.
"""

from pipeline import MedicalDataExtractor
from pathlib import Path


def example_single_file():
    """Example: Extract data from a single file."""
    print("="*60)
    print("Example 1: Single File Extraction")
    print("="*60)

    # Initialize extractor
    extractor = MedicalDataExtractor(
        model="llava:latest",  # or "llava:13b" for better quality
        output_dir="output",
        dpi=200
    )

    # Process a single file
    result = extractor.extract_from_file(
        file_path="path/to/medical_report.pdf",
        save_output=True
    )

    if result['success']:
        print(f"Success! Output: {result['output_file']}")
        print(f"Content preview:\n{result['content'][:500]}...")
    else:
        print(f"Failed: {result['error']}")


def example_directory_batch():
    """Example: Extract data from all files in a directory."""
    print("\n" + "="*60)
    print("Example 2: Batch Processing from Directory")
    print("="*60)

    # Initialize extractor
    extractor = MedicalDataExtractor(
        model="llava:latest",
        output_dir="batch_output",
        dpi=200
    )

    # Process all files in directory
    result = extractor.extract_from_directory(
        directory="path/to/medical_records",
        create_index=True,
        create_summary=True
    )

    print(f"\nProcessed {result['total']} files")
    print(f"Successful: {result['successful']}")
    print(f"Failed: {result['failed']}")


def example_custom_prompt():
    """Example: Use custom extraction prompt."""
    print("\n" + "="*60)
    print("Example 3: Custom Extraction Prompt")
    print("="*60)

    extractor = MedicalDataExtractor()

    custom_prompt = """
    Extract ONLY the following information from this medical document:
    - Patient name and ID
    - Date of visit
    - Primary diagnosis
    - Prescribed medications

    Format in markdown with clear sections. Do not use bold or italic.
    """

    result = extractor.extract_from_file(
        file_path="path/to/medical_report.pdf",
        custom_prompt=custom_prompt,
        save_output=True
    )

    if result['success']:
        print(f"Custom extraction complete: {result['output_file']}")


def example_file_list():
    """Example: Process a specific list of files."""
    print("\n" + "="*60)
    print("Example 4: Process Specific File List")
    print("="*60)

    extractor = MedicalDataExtractor(output_dir="selected_output")

    # List of specific files to process
    files_to_process = [
        "path/to/report1.pdf",
        "path/to/report2.pdf",
        "path/to/scan1.jpg",
        "path/to/scan2.png"
    ]

    result = extractor.extract_from_file_list(
        file_paths=files_to_process,
        create_index=True,
        create_summary=True
    )

    print(f"\nProcessed {result['successful']} out of {result['total']} files")


def example_different_models():
    """Example: Compare different vision models."""
    print("\n" + "="*60)
    print("Example 5: Using Different Models")
    print("="*60)

    test_file = "path/to/test_report.pdf"

    # Try different models
    models = ["llava:latest", "llava:13b", "llava:34b"]

    for model in models:
        print(f"\nTesting with model: {model}")

        try:
            extractor = MedicalDataExtractor(
                model=model,
                output_dir=f"output_{model.replace(':', '_')}"
            )

            result = extractor.extract_from_file(
                file_path=test_file,
                save_output=True,
                output_filename=f"extracted_{model.replace(':', '_')}.md"
            )

            if result['success']:
                print(f"  Success: {result['output_file']}")
            else:
                print(f"  Failed: {result['error']}")

        except Exception as e:
            print(f"  Error with {model}: {e}")


def example_high_quality_extraction():
    """Example: High-quality extraction with optimal settings."""
    print("\n" + "="*60)
    print("Example 6: High-Quality Extraction")
    print("="*60)

    # Use higher DPI and larger model for best quality
    extractor = MedicalDataExtractor(
        model="llava:13b",  # Larger model for better accuracy
        output_dir="high_quality_output",
        dpi=300  # Higher DPI for better image quality
    )

    detailed_prompt = """
    Perform a comprehensive extraction of all medical information from this document.
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

    result = extractor.extract_from_file(
        file_path="path/to/comprehensive_medical_record.pdf",
        custom_prompt=detailed_prompt,
        save_output=True
    )

    if result['success']:
        print(f"High-quality extraction complete!")
        print(f"Pages processed: {result['num_pages']}")
        print(f"Output: {result['output_file']}")


def example_pii_redaction():
    """Example: Extract with PII redaction."""
    print("\n" + "="*60)
    print("Example 7: PII Redaction")
    print("="*60)

    # Extract with automatic redaction (default)
    extractor = MedicalDataExtractor(
        enable_redaction=True,
        redaction_marker="[REDACTED]"
    )

    result = extractor.extract_from_file(
        file_path="path/to/medical_report.pdf",
        save_output=True
    )

    if result['success']:
        print(f"Extraction complete: {result['output_file']}")
        print(f"PII items redacted: {result['redaction_count']}")


def example_selective_redaction():
    """Example: Redact only specific PII types."""
    print("\n" + "="*60)
    print("Example 8: Selective PII Redaction")
    print("="*60)

    from pii_redactor import PIIRedactor

    # Create redactor
    redactor = PIIRedactor(redaction_marker="[###]")

    # Read a markdown file
    with open("path/to/extracted_document.md", 'r') as f:
        content = f.read()

    # Redact only names and contact info (keep IDs and DOB)
    redacted = redactor.redact_all(
        content,
        include={'names', 'contact'},
        exclude={'ids', 'dob'}
    )

    # Save redacted version
    with open("path/to/redacted_document.md", 'w') as f:
        f.write(redacted)

    # Get redaction summary
    summary = redactor.get_redaction_summary()
    print(f"Redacted {summary['total_redactions']} items")
    print(f"By type: {summary['by_type']}")


def example_no_redaction():
    """Example: Extract without PII redaction."""
    print("\n" + "="*60)
    print("Example 9: Disable PII Redaction")
    print("="*60)

    # Disable redaction for research or development purposes
    extractor = MedicalDataExtractor(
        enable_redaction=False  # Keep all original data
    )

    result = extractor.extract_from_file(
        file_path="path/to/medical_report.pdf",
        save_output=True
    )

    print("Extraction complete without redaction")
    print("WARNING: Output contains unredacted PII!")


if __name__ == '__main__':
    print("\nMedical Data Extractor - Example Usage\n")

    # Uncomment the examples you want to run:

    # example_single_file()
    # example_directory_batch()
    # example_custom_prompt()
    # example_file_list()
    # example_different_models()
    # example_high_quality_extraction()
    # example_pii_redaction()
    # example_selective_redaction()
    # example_no_redaction()

    print("\n\nTo run examples, uncomment the function calls in example_usage.py")
    print("Make sure to update the file paths to point to your actual medical documents.")
