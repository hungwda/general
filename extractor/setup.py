"""
Setup configuration for Medical Data Extractor.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="medical-data-extractor",
    version="1.0.0",
    description="Privacy-first local pipeline for extracting medical data from PDFs and images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Medical Data Extractor Team",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "ollama>=0.2.0",
        "Pillow>=10.0.0",
        "pymupdf>=1.23.0",
        "pdf2image>=1.16.3",
        "pathlib>=1.0.1",
        "python-dotenv>=1.0.0",
        "tqdm>=4.66.0",
    ],
    entry_points={
        "console_scripts": [
            "medical-extractor=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="medical, data extraction, pdf, ocr, llm, ollama, vision, privacy",
)
