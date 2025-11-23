"""Image Generation Agent - Creates panel images using Gemini Imagen API."""
import time
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from google import genai
from google.genai import types
from models import ImagePrompt, GeneratedPanel, Panel
from config import Config


class ImageGeneratorAgent:
    """Agent responsible for generating comic panel images."""

    def __init__(self, client):
        """Initialize Image Generator Agent.

        Args:
            client: Google GenAI client instance
        """
        self.client = client
        self.output_dir = Config.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chat = None

    def initialize_chat(self):
        """Initialize a multi-turn chat for consistent image generation."""
        try:
            self.chat = self.client.chats.create(
                model=Config.GEMINI_IMAGE_MODEL,
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE', 'TEXT'],
                )
            )
        except Exception as e:
            print(f"Warning: Could not initialize chat session: {e}")
            print("Will use single-turn generation instead")
            self.chat = None

    def generate_panel_image(
        self,
        panel: Panel,
        prompt: ImagePrompt,
        session_id: str,
        retry_count: int = 3
    ) -> GeneratedPanel:
        """Generate image for a single panel.

        Args:
            panel: Panel data
            prompt: Image generation prompt
            session_id: Unique session identifier
            retry_count: Number of retries on failure

        Returns:
            GeneratedPanel: Panel with generated image
        """
        for attempt in range(retry_count):
            try:
                # Generate image
                if self.chat:
                    response = self._generate_with_chat(prompt.full_prompt)
                else:
                    response = self._generate_single(prompt.full_prompt)

                # Save image
                image_path = self._save_image(
                    response,
                    session_id,
                    panel.number
                )

                # Create GeneratedPanel
                generated_panel = GeneratedPanel(
                    panel=panel,
                    image_path=str(image_path),
                    prompt_used=prompt.full_prompt,
                    metadata={
                        "panel_number": panel.number,
                        "characters": panel.characters,
                        "attempt": attempt + 1,
                        "generation_time": datetime.now().isoformat()
                    }
                )

                return generated_panel

            except Exception as e:
                print(f"Attempt {attempt + 1} failed for panel {panel.number}: {e}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise RuntimeError(
                        f"Failed to generate image for panel {panel.number} after {retry_count} attempts"
                    )

    def _generate_with_chat(self, prompt: str):
        """Generate image using multi-turn chat for consistency.

        Args:
            prompt: Image generation prompt

        Returns:
            Response with generated image
        """
        response = self.chat.send_message(prompt)
        return response

    def _generate_single(self, prompt: str):
        """Generate image using single-turn request.

        Args:
            prompt: Image generation prompt

        Returns:
            Response with generated image
        """
        response = self.client.models.generate_content(
            model=Config.GEMINI_IMAGE_MODEL,
            contents=[prompt],
        )
        return response

    def _save_image(
        self,
        response,
        session_id: str,
        panel_number: int
    ) -> Path:
        """Save generated image to disk.

        Args:
            response: API response containing image
            session_id: Session identifier
            panel_number: Panel number

        Returns:
            Path: Path to saved image
        """
        # Extract image from response
        image = None
        for part in response.parts:
            if hasattr(part, 'inline_data') and part.inline_data is not None:
                try:
                    image = part.as_image()
                    break
                except:
                    pass

        if image is None:
            raise ValueError("No image found in response")

        # Create filename
        filename = f"{session_id}_panel_{panel_number}.png"
        image_path = self.output_dir / filename

        # Save image
        image.save(image_path)
        print(f"✓ Saved panel {panel_number} to {image_path}")

        return image_path

    def generate_all_panels(
        self,
        panels: List[Panel],
        prompts: List[ImagePrompt],
        session_id: str
    ) -> List[GeneratedPanel]:
        """Generate images for all panels sequentially.

        Args:
            panels: List of panels
            prompts: List of image prompts
            session_id: Session identifier

        Returns:
            List[GeneratedPanel]: All generated panels
        """
        # Initialize chat for consistency
        self.initialize_chat()

        generated_panels = []

        for panel, prompt in zip(panels, prompts):
            print(f"Generating panel {panel.number}/{len(panels)}...")

            generated_panel = self.generate_panel_image(
                panel=panel,
                prompt=prompt,
                session_id=session_id
            )

            generated_panels.append(generated_panel)

        return generated_panels

    def refine_panel(
        self,
        panel: GeneratedPanel,
        refinement_instructions: str,
        session_id: str
    ) -> GeneratedPanel:
        """Refine a generated panel based on feedback.

        Args:
            panel: Original generated panel
            refinement_instructions: Instructions for refinement
            session_id: Session identifier

        Returns:
            GeneratedPanel: Refined panel
        """
        # Build refinement prompt
        prompt = f"""Based on the previous image, make these changes:
{refinement_instructions}

Maintain the same characters and overall style, but adjust as requested.
Keep it in Calvin and Hobbes style."""

        # Generate refined version
        if self.chat:
            response = self._generate_with_chat(prompt)
        else:
            # Include original prompt context for single-turn
            full_context = f"{panel.prompt_used}\n\nRefinement: {prompt}"
            response = self._generate_single(full_context)

        # Save refined image
        image_path = self._save_image(
            response,
            f"{session_id}_refined",
            panel.panel.number
        )

        # Create refined panel
        refined_panel = GeneratedPanel(
            panel=panel.panel,
            image_path=str(image_path),
            prompt_used=f"{panel.prompt_used}\n[Refined: {refinement_instructions}]",
            metadata={
                **panel.metadata,
                "refined": True,
                "refinement_instructions": refinement_instructions,
                "original_image": panel.image_path
            }
        )

        return refined_panel
