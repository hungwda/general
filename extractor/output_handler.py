"""
Output handler for saving extracted medical data in markdown format.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class OutputHandler:
    """Handles saving extracted medical data to markdown files."""

    def __init__(self, output_dir: str = "output"):
        """
        Initialize output handler.

        Args:
            output_dir: Directory to save extracted data (default: 'output')
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to be safe for file systems.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove or replace unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')

        # Limit length
        if len(filename) > 200:
            filename = filename[:200]

        return filename

    def generate_output_filename(self, source_file: Path) -> str:
        """
        Generate output filename based on source file.

        Args:
            source_file: Original source file path

        Returns:
            Output filename with .md extension
        """
        # Get base name without extension
        base_name = source_file.stem

        # Sanitize
        safe_name = self.sanitize_filename(base_name)

        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return f"{safe_name}_{timestamp}.md"

    def save_extraction(self, content: str, source_file: Path,
                       custom_filename: Optional[str] = None) -> Path:
        """
        Save extracted content to markdown file.

        Args:
            content: Extracted markdown content
            source_file: Original source file path
            custom_filename: Optional custom output filename

        Returns:
            Path to saved file
        """
        # Determine output filename
        if custom_filename:
            output_filename = custom_filename if custom_filename.endswith('.md') else f"{custom_filename}.md"
        else:
            output_filename = self.generate_output_filename(source_file)

        # Full output path
        output_path = self.output_dir / output_filename

        # Add metadata header
        metadata = self._generate_metadata_header(source_file)
        full_content = metadata + "\n\n" + content

        # Save to file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            print(f"Saved extraction to: {output_path}")
            return output_path
        except Exception as e:
            print(f"Error saving file {output_path}: {e}")
            raise

    def _generate_metadata_header(self, source_file: Path) -> str:
        """
        Generate metadata header for extracted document.

        Args:
            source_file: Original source file path

        Returns:
            Markdown metadata header
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        metadata = f"""<!--
Extraction Metadata:
- Source File: {source_file.name}
- Source Path: {source_file.absolute()}
- Extraction Date: {timestamp}
- Extractor: Medical Data Extractor v1.0
-->"""

        return metadata

    def save_batch_summary(self, results: dict, summary_filename: str = "extraction_summary.md") -> Path:
        """
        Save summary of batch extraction results.

        Args:
            results: Dictionary mapping source files to extraction results
            summary_filename: Name of summary file

        Returns:
            Path to summary file
        """
        summary_path = self.output_dir / summary_filename

        # Build summary content
        summary_content = "# Batch Extraction Summary\n\n"
        summary_content += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        summary_content += f"Total Files Processed: {len(results)}\n\n"
        summary_content += "## Processed Files\n\n"

        for i, (source_file, result) in enumerate(results.items(), 1):
            summary_content += f"{i}. {source_file}\n"
            if result.get('success'):
                summary_content += f"   - Status: Success\n"
                summary_content += f"   - Output: {result.get('output_file', 'N/A')}\n"
            else:
                summary_content += f"   - Status: Failed\n"
                summary_content += f"   - Error: {result.get('error', 'Unknown error')}\n"
            summary_content += "\n"

        # Save summary
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            print(f"Saved batch summary to: {summary_path}")
            return summary_path
        except Exception as e:
            print(f"Error saving summary file {summary_path}: {e}")
            raise

    def create_index(self, results: dict, index_filename: str = "index.md") -> Path:
        """
        Create an index file linking to all extracted documents.

        Args:
            results: Dictionary mapping source files to extraction results
            index_filename: Name of index file

        Returns:
            Path to index file
        """
        index_path = self.output_dir / index_filename

        # Build index content
        index_content = "# Medical Data Extraction Index\n\n"
        index_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        index_content += f"Total Documents: {len(results)}\n\n"
        index_content += "## Extracted Documents\n\n"

        for i, (source_file, result) in enumerate(results.items(), 1):
            if result.get('success'):
                output_file = Path(result.get('output_file', ''))
                relative_path = output_file.name
                index_content += f"{i}. [{source_file}]({relative_path})\n"
            else:
                index_content += f"{i}. {source_file} - Failed to extract\n"

        # Save index
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            print(f"Created index at: {index_path}")
            return index_path
        except Exception as e:
            print(f"Error creating index file {index_path}: {e}")
            raise
