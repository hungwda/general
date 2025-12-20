"""
Medical Data Extractor

A privacy-first local pipeline for extracting medical data from PDFs and images
using Ollama vision models.
"""

from .pipeline import MedicalDataExtractor
from .document_processor import DocumentProcessor
from .llm_extractor import LLMExtractor
from .output_handler import OutputHandler
from .config import Config

__version__ = "1.0.0"
__author__ = "Medical Data Extractor Team"

__all__ = [
    "MedicalDataExtractor",
    "DocumentProcessor",
    "LLMExtractor",
    "OutputHandler",
    "Config",
]
