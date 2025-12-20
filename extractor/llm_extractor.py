"""
LLM-based extractor using Ollama vision models for medical data extraction.
"""

import io
import base64
from typing import List, Dict, Optional
from PIL import Image
import ollama


class LLMExtractor:
    """Extracts structured medical data using local Ollama vision models."""

    def __init__(self, model: str = "llava:latest", ollama_host: Optional[str] = None):
        """
        Initialize LLM extractor.

        Args:
            model: Ollama vision model name (default: llava:latest)
            ollama_host: Optional Ollama host URL
        """
        self.model = model
        self.ollama_host = ollama_host

        # System prompt for medical data extraction
        self.system_prompt = """You are a medical data extraction assistant. Your task is to extract all relevant medical information from documents and format them in clean markdown.

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

    def image_to_base64(self, image: Image.Image) -> str:
        """
        Convert PIL Image to base64 string.

        Args:
            image: PIL Image object

        Returns:
            Base64 encoded image string
        """
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')

    def extract_from_image(self, image: Image.Image, custom_prompt: Optional[str] = None) -> str:
        """
        Extract medical data from a single image using vision model.

        Args:
            image: PIL Image object
            custom_prompt: Optional custom extraction prompt

        Returns:
            Extracted text in markdown format
        """
        try:
            # Convert image to base64
            img_base64 = self.image_to_base64(image)

            # Prepare the prompt
            user_prompt = custom_prompt or "Extract all medical information from this document and format it in clean markdown. Do not use bold or italic formatting. Use tables where appropriate."

            # Create messages for the vision model
            messages = [
                {
                    'role': 'system',
                    'content': self.system_prompt
                },
                {
                    'role': 'user',
                    'content': user_prompt,
                    'images': [img_base64]
                }
            ]

            # Call Ollama API
            response = ollama.chat(
                model=self.model,
                messages=messages
            )

            return response['message']['content']

        except Exception as e:
            return f"Error extracting from image: {e}"

    def extract_from_images(self, images: List[Image.Image],
                           combine_pages: bool = True,
                           custom_prompt: Optional[str] = None) -> str:
        """
        Extract medical data from multiple images (e.g., multi-page PDF).

        Args:
            images: List of PIL Image objects
            combine_pages: If True, combine all page extractions into one document
            custom_prompt: Optional custom extraction prompt

        Returns:
            Extracted text in markdown format
        """
        if not images:
            return "No images to process"

        extractions = []

        for i, image in enumerate(images):
            print(f"Processing page {i + 1}/{len(images)}...")

            # For multi-page documents, add page context to prompt
            if len(images) > 1 and custom_prompt is None:
                page_prompt = f"Extract all medical information from this document (page {i + 1} of {len(images)}) and format it in clean markdown. Do not use bold or italic formatting."
            else:
                page_prompt = custom_prompt

            extraction = self.extract_from_image(image, page_prompt)
            extractions.append(extraction)

        if combine_pages and len(extractions) > 1:
            # Combine all pages into a single document
            combined = self._combine_pages(extractions)
            return combined
        elif len(extractions) == 1:
            return extractions[0]
        else:
            # Return separate page extractions
            result = ""
            for i, extraction in enumerate(extractions):
                result += f"# Page {i + 1}\n\n{extraction}\n\n---\n\n"
            return result

    def _combine_pages(self, page_extractions: List[str]) -> str:
        """
        Intelligently combine multiple page extractions into a single document.

        Args:
            page_extractions: List of markdown extractions from each page

        Returns:
            Combined markdown document
        """
        # Simple combination - join all pages
        # In a more advanced version, this could use LLM to merge duplicate sections
        combined = "# Medical Document\n\n"

        for i, extraction in enumerate(page_extractions):
            # Remove duplicate headers if the extraction already has them
            if i > 0 and extraction.startswith("# Medical Document"):
                extraction = extraction.replace("# Medical Document", "", 1).strip()

            combined += extraction
            if i < len(page_extractions) - 1:
                combined += "\n\n"

        return combined

    def post_process_markdown(self, markdown_text: str) -> str:
        """
        Post-process extracted markdown to ensure no bold/italic formatting.

        Args:
            markdown_text: Raw markdown text

        Returns:
            Cleaned markdown text
        """
        # Remove bold formatting
        text = markdown_text.replace("**", "")

        # Remove italic formatting
        text = text.replace("*", "")
        text = text.replace("_", "")

        return text
