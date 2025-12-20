"""
Document processor for handling PDF and image files.
Converts documents to images for vision model processing.
"""

import os
from pathlib import Path
from typing import List, Union
from PIL import Image
import fitz  # PyMuPDF


class DocumentProcessor:
    """Processes medical documents (PDFs and images) for extraction."""

    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    SUPPORTED_PDF_FORMAT = '.pdf'

    def __init__(self, dpi: int = 200):
        """
        Initialize document processor.

        Args:
            dpi: Resolution for PDF to image conversion (default: 200)
        """
        self.dpi = dpi

    def is_supported_file(self, file_path: Path) -> bool:
        """Check if file format is supported."""
        suffix = file_path.suffix.lower()
        return suffix in self.SUPPORTED_IMAGE_FORMATS or suffix == self.SUPPORTED_PDF_FORMAT

    def process_pdf(self, pdf_path: Path) -> List[Image.Image]:
        """
        Convert PDF pages to images.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of PIL Images, one per page
        """
        images = []

        try:
            pdf_document = fitz.open(str(pdf_path))

            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]

                # Calculate zoom factor for desired DPI
                zoom = self.dpi / 72  # 72 is default DPI
                mat = fitz.Matrix(zoom, zoom)

                # Render page to image
                pix = page.get_pixmap(matrix=mat)

                # Convert to PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)

            pdf_document.close()

        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {e}")

        return images

    def process_image(self, image_path: Path) -> List[Image.Image]:
        """
        Load image file.

        Args:
            image_path: Path to image file

        Returns:
            List containing single PIL Image
        """
        try:
            img = Image.open(image_path)
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            return [img]
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return []

    def process_document(self, file_path: Union[str, Path]) -> List[Image.Image]:
        """
        Process a document file (PDF or image) and return images.

        Args:
            file_path: Path to document file

        Returns:
            List of PIL Images
        """
        file_path = Path(file_path)

        if not file_path.exists():
            print(f"File not found: {file_path}")
            return []

        if not self.is_supported_file(file_path):
            print(f"Unsupported file format: {file_path.suffix}")
            return []

        suffix = file_path.suffix.lower()

        if suffix == self.SUPPORTED_PDF_FORMAT:
            return self.process_pdf(file_path)
        elif suffix in self.SUPPORTED_IMAGE_FORMATS:
            return self.process_image(file_path)

        return []

    def process_directory(self, directory: Union[str, Path]) -> dict:
        """
        Process all supported documents in a directory.

        Args:
            directory: Path to directory containing documents

        Returns:
            Dictionary mapping file paths to lists of images
        """
        directory = Path(directory)
        results = {}

        if not directory.exists() or not directory.is_dir():
            print(f"Invalid directory: {directory}")
            return results

        # Find all supported files
        for file_path in directory.rglob('*'):
            if file_path.is_file() and self.is_supported_file(file_path):
                images = self.process_document(file_path)
                if images:
                    results[str(file_path)] = images

        return results
