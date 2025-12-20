#!/usr/bin/env python3
"""
Medical Data Extractor - Main Entry Point

A privacy-first local pipeline for extracting medical data from PDFs and images
using Ollama vision models.
"""

import argparse
import sys
from pathlib import Path

from pipeline import MedicalDataExtractor


def main():
    """Main entry point for the medical data extractor."""

    parser = argparse.ArgumentParser(
        description='Extract medical data from PDF and image documents using local LLM vision models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Extract from a single file:
    python main.py --file medical_report.pdf

  Extract from all files in a directory:
    python main.py --directory ./medical_records

  Use a specific Ollama model:
    python main.py --file report.pdf --model llava:13b

  Specify custom output directory:
    python main.py --directory ./records --output ./extracted_data

  Use custom extraction prompt:
    python main.py --file report.pdf --prompt "Extract only patient demographics and diagnoses"
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--file', '-f',
        type=str,
        help='Path to a single PDF or image file to process'
    )
    input_group.add_argument(
        '--directory', '-d',
        type=str,
        help='Path to directory containing documents to process'
    )

    # Model options
    parser.add_argument(
        '--model', '-m',
        type=str,
        default='llava:latest',
        help='Ollama vision model to use (default: llava:latest)'
    )

    # Output options
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='output',
        help='Output directory for extracted data (default: output)'
    )

    parser.add_argument(
        '--output-filename',
        type=str,
        help='Custom filename for single file extraction (optional)'
    )

    # Processing options
    parser.add_argument(
        '--dpi',
        type=int,
        default=200,
        help='DPI for PDF to image conversion (default: 200)'
    )

    parser.add_argument(
        '--prompt',
        type=str,
        help='Custom extraction prompt (optional)'
    )

    parser.add_argument(
        '--no-index',
        action='store_true',
        help='Do not create index file for batch processing'
    )

    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='Do not create summary file for batch processing'
    )

    # Ollama options
    parser.add_argument(
        '--ollama-host',
        type=str,
        help='Ollama host URL (optional, defaults to local)'
    )

    args = parser.parse_args()

    # Initialize the extractor
    print("\nInitializing Medical Data Extractor...")
    print(f"Model: {args.model}")
    print(f"Output Directory: {args.output}")
    print(f"DPI: {args.dpi}\n")

    try:
        extractor = MedicalDataExtractor(
            model=args.model,
            output_dir=args.output,
            dpi=args.dpi,
            ollama_host=args.ollama_host
        )

        # Process based on input type
        if args.file:
            # Single file extraction
            result = extractor.extract_from_file(
                file_path=args.file,
                custom_prompt=args.prompt,
                save_output=True,
                output_filename=args.output_filename
            )

            if result['success']:
                print(f"\nExtraction successful!")
                print(f"Output saved to: {result['output_file']}")
                return 0
            else:
                print(f"\nExtraction failed: {result.get('error', 'Unknown error')}")
                return 1

        elif args.directory:
            # Directory batch extraction
            result = extractor.extract_from_directory(
                directory=args.directory,
                custom_prompt=args.prompt,
                create_index=not args.no_index,
                create_summary=not args.no_summary
            )

            if result['success']:
                print(f"\nBatch extraction completed successfully!")
                print(f"Output directory: {args.output}")
                return 0
            else:
                print(f"\nBatch extraction failed: {result.get('error', 'Unknown error')}")
                return 1

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
