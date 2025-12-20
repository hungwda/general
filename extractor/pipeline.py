"""
Main pipeline for medical data extraction from documents.
"""

from pathlib import Path
from typing import Union, List, Optional, Dict
from tqdm import tqdm

from document_processor import DocumentProcessor
from llm_extractor import LLMExtractor
from output_handler import OutputHandler
from pii_redactor import PIIRedactor


class MedicalDataExtractor:
    """
    Main pipeline for extracting medical data from PDF and image documents.
    Uses local Ollama vision models for privacy-first processing.
    """

    def __init__(
        self,
        model: str = "llava:latest",
        output_dir: str = "output",
        dpi: int = 200,
        ollama_host: Optional[str] = None,
        enable_redaction: bool = True,
        redaction_marker: str = "[REDACTED]"
    ):
        """
        Initialize medical data extraction pipeline.

        Args:
            model: Ollama vision model name (default: llava:latest)
            output_dir: Directory for output files (default: 'output')
            dpi: DPI for PDF to image conversion (default: 200)
            ollama_host: Optional Ollama host URL
            enable_redaction: Enable automatic PII redaction (default: True)
            redaction_marker: Text to replace PII with (default: [REDACTED])
        """
        self.document_processor = DocumentProcessor(dpi=dpi)
        self.llm_extractor = LLMExtractor(model=model, ollama_host=ollama_host)
        self.output_handler = OutputHandler(output_dir=output_dir)
        self.enable_redaction = enable_redaction
        self.pii_redactor = PIIRedactor(
            redaction_marker=redaction_marker,
            preserve_structure=True,
            log_redactions=True
        )

    def extract_from_file(
        self,
        file_path: Union[str, Path],
        custom_prompt: Optional[str] = None,
        save_output: bool = True,
        output_filename: Optional[str] = None,
        redact_pii: Optional[bool] = None,
        redact_include: Optional[set] = None,
        redact_exclude: Optional[set] = None
    ) -> Dict:
        """
        Extract medical data from a single file.

        Args:
            file_path: Path to PDF or image file
            custom_prompt: Optional custom extraction prompt
            save_output: Whether to save output to file (default: True)
            output_filename: Optional custom output filename
            redact_pii: Override global redaction setting (None = use global)
            redact_include: Specific PII types to redact (None = all)
            redact_exclude: PII types to skip redacting

        Returns:
            Dictionary containing extraction results
        """
        file_path = Path(file_path)

        print(f"\nProcessing: {file_path.name}")

        # Step 1: Process document to images
        print("Step 1: Converting document to images...")
        images = self.document_processor.process_document(file_path)

        if not images:
            return {
                'success': False,
                'error': 'Failed to process document',
                'file': str(file_path)
            }

        print(f"Converted to {len(images)} image(s)")

        # Step 2: Extract data using LLM
        print("Step 2: Extracting medical data using vision model...")
        extracted_text = self.llm_extractor.extract_from_images(
            images,
            combine_pages=True,
            custom_prompt=custom_prompt
        )

        # Step 3: Post-process to remove bold/italic
        print("Step 3: Post-processing markdown...")
        cleaned_text = self.llm_extractor.post_process_markdown(extracted_text)

        # Step 4: Save output
        output_path = None
        if save_output:
            print("Step 4: Saving output...")
            output_path = self.output_handler.save_extraction(
                cleaned_text,
                file_path,
                output_filename
            )

        # Step 5: Redact PII if enabled
        redaction_count = 0
        should_redact = redact_pii if redact_pii is not None else self.enable_redaction

        if should_redact and output_path:
            print("Step 5: Redacting PII from extracted data...")
            output_path, redaction_count = self.pii_redactor.redact_file(
                output_path,
                output_path,
                include=redact_include,
                exclude=redact_exclude
            )
            print(f"Redacted {redaction_count} PII items")

        print(f"Extraction complete for {file_path.name}")

        return {
            'success': True,
            'file': str(file_path),
            'output_file': str(output_path) if output_path else None,
            'content': cleaned_text,
            'num_pages': len(images),
            'pii_redacted': should_redact,
            'redaction_count': redaction_count
        }

    def extract_from_directory(
        self,
        directory: Union[str, Path],
        custom_prompt: Optional[str] = None,
        create_index: bool = True,
        create_summary: bool = True
    ) -> Dict:
        """
        Extract medical data from all supported files in a directory.

        Args:
            directory: Path to directory containing documents
            custom_prompt: Optional custom extraction prompt
            create_index: Whether to create index file (default: True)
            create_summary: Whether to create summary file (default: True)

        Returns:
            Dictionary containing batch extraction results
        """
        directory = Path(directory)

        print(f"\n{'='*60}")
        print(f"Batch Extraction from: {directory}")
        print(f"{'='*60}\n")

        # Find all supported files
        supported_files = []
        for file_path in directory.rglob('*'):
            if file_path.is_file() and self.document_processor.is_supported_file(file_path):
                supported_files.append(file_path)

        if not supported_files:
            print("No supported files found in directory")
            return {'success': False, 'error': 'No supported files found'}

        print(f"Found {len(supported_files)} file(s) to process\n")

        # Process each file
        results = {}

        for file_path in tqdm(supported_files, desc="Processing documents", unit="file"):
            try:
                result = self.extract_from_file(
                    file_path,
                    custom_prompt=custom_prompt,
                    save_output=True
                )
                results[str(file_path)] = result

            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                results[str(file_path)] = {
                    'success': False,
                    'error': str(e),
                    'file': str(file_path)
                }

        # Create summary and index
        if create_summary:
            print("\nCreating batch summary...")
            self.output_handler.save_batch_summary(results)

        if create_index:
            print("Creating document index...")
            self.output_handler.create_index(results)

        # Calculate statistics
        successful = sum(1 for r in results.values() if r.get('success'))
        failed = len(results) - successful

        print(f"\n{'='*60}")
        print(f"Batch Extraction Complete")
        print(f"{'='*60}")
        print(f"Total files: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"{'='*60}\n")

        return {
            'success': True,
            'total': len(results),
            'successful': successful,
            'failed': failed,
            'results': results
        }

    def extract_from_file_list(
        self,
        file_paths: List[Union[str, Path]],
        custom_prompt: Optional[str] = None,
        create_index: bool = True,
        create_summary: bool = True
    ) -> Dict:
        """
        Extract medical data from a list of files.

        Args:
            file_paths: List of file paths to process
            custom_prompt: Optional custom extraction prompt
            create_index: Whether to create index file (default: True)
            create_summary: Whether to create summary file (default: True)

        Returns:
            Dictionary containing batch extraction results
        """
        print(f"\n{'='*60}")
        print(f"Batch Extraction from File List")
        print(f"{'='*60}\n")
        print(f"Processing {len(file_paths)} file(s)\n")

        # Process each file
        results = {}

        for file_path in tqdm(file_paths, desc="Processing documents", unit="file"):
            try:
                result = self.extract_from_file(
                    file_path,
                    custom_prompt=custom_prompt,
                    save_output=True
                )
                results[str(file_path)] = result

            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                results[str(file_path)] = {
                    'success': False,
                    'error': str(e),
                    'file': str(file_path)
                }

        # Create summary and index
        if create_summary:
            print("\nCreating batch summary...")
            self.output_handler.save_batch_summary(results)

        if create_index:
            print("Creating document index...")
            self.output_handler.create_index(results)

        # Calculate statistics
        successful = sum(1 for r in results.values() if r.get('success'))
        failed = len(results) - successful

        print(f"\n{'='*60}")
        print(f"Batch Extraction Complete")
        print(f"{'='*60}")
        print(f"Total files: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"{'='*60}\n")

        return {
            'success': True,
            'total': len(results),
            'successful': successful,
            'failed': failed,
            'results': results
        }
