"""Image generation tool using Gemini Imagen API."""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from google import genai
from google.genai import types


class ImageGenerationTool:
    """Tool for generating comic panel images using Gemini."""

    def __init__(self, api_key: str, output_dir: str = "output"):
        """Initialize image generation tool.

        Args:
            api_key: Google API key
            output_dir: Directory for output images
        """
        self.client = genai.Client(api_key=api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chat = None

    def initialize_chat(self):
        """Initialize multi-turn chat for consistent generation."""
        try:
            self.chat = self.client.chats.create(
                model="gemini-2.0-flash-exp",
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE', 'TEXT'],
                )
            )
            print("✓ Initialized image generation chat session")
        except Exception as e:
            print(f"Warning: Could not initialize chat: {e}")
            self.chat = None

    def generate_panel_images(self, scene_prompts: list, session_id: str) -> Dict[str, Any]:
        """Generate images for all panels.

        Args:
            scene_prompts: List of scene prompt objects
            session_id: Unique session identifier

        Returns:
            Dict with generation results
        """
        # Initialize chat for consistency
        self.initialize_chat()

        generated_panels = []

        for prompt_data in scene_prompts:
            panel_num = prompt_data['panel_number']
            prompt = prompt_data['prompt']

            print(f"\nGenerating panel {panel_num}...")
            print(f"Prompt: {prompt[:100]}...")

            try:
                # Generate image
                if self.chat:
                    response = self.chat.send_message(prompt)
                else:
                    response = self.client.models.generate_content(
                        model="gemini-2.0-flash-exp",
                        contents=[prompt]
                    )

                # Save image
                image_path = self._save_image(response, session_id, panel_num)

                generated_panels.append({
                    "panel_number": panel_num,
                    "image_path": str(image_path),
                    "prompt_used": prompt,
                    "characters": prompt_data.get('characters', []),
                    "setting": prompt_data.get('setting', 'unknown'),
                    "status": "success"
                })

                print(f"✓ Panel {panel_num} generated: {image_path}")

            except Exception as e:
                print(f"✗ Failed to generate panel {panel_num}: {e}")
                generated_panels.append({
                    "panel_number": panel_num,
                    "status": "failed",
                    "error": str(e)
                })

        return {
            "generated_panels": generated_panels,
            "total_panels": len(scene_prompts),
            "successful": len([p for p in generated_panels if p['status'] == 'success']),
            "session_id": session_id
        }

    def _save_image(self, response, session_id: str, panel_number: int) -> Path:
        """Save generated image to disk.

        Args:
            response: API response with image
            session_id: Session ID
            panel_number: Panel number

        Returns:
            Path to saved image
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

        # Save image
        filename = f"{session_id}_panel_{panel_number}.png"
        image_path = self.output_dir / filename
        image.save(image_path)

        return image_path

    def assemble_comic(
        self,
        generated_panels: list,
        story_plan: dict,
        session_id: str
    ) -> str:
        """Assemble individual panels into final comic strip.

        Args:
            generated_panels: List of generated panel data
            story_plan: Original story plan
            session_id: Session ID

        Returns:
            Path to final assembled comic
        """
        from PIL import Image, ImageDraw, ImageFont

        # Filter successful panels
        successful_panels = [p for p in generated_panels if p['status'] == 'success']

        if not successful_panels:
            raise ValueError("No successful panels to assemble")

        # Load panel images
        panel_images = []
        for panel_data in sorted(successful_panels, key=lambda x: x['panel_number']):
            img = Image.open(panel_data['image_path'])
            # Resize to standard size
            img = img.resize((800, 450), Image.Resampling.LANCZOS)
            panel_images.append(img)

        # Calculate canvas size
        panel_width = 800
        panel_height = 450
        spacing = 20
        border = 10

        num_panels = len(panel_images)
        canvas_width = (panel_width + border * 2) * num_panels + spacing * (num_panels + 1)
        canvas_height = panel_height + border * 2 + spacing * 2 + 80  # Extra for title

        # Create canvas
        canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
        draw = ImageDraw.Draw(canvas)

        # Add title
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        except:
            font = ImageFont.load_default()

        title = story_plan.get('title', 'Comic Strip')
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        title_x = (canvas_width - text_width) // 2
        draw.text((title_x, spacing), title, fill='black', font=font)

        # Paste panels
        y_offset = spacing + 60
        x_offset = spacing

        for img in panel_images:
            # Add border
            bordered = Image.new('RGB', (panel_width + border * 2, panel_height + border * 2), 'black')
            bordered.paste(img, (border, border))

            # Paste to canvas
            canvas.paste(bordered, (x_offset, y_offset))
            x_offset += panel_width + border * 2 + spacing

        # Save final comic
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_path = self.output_dir / f"comic_{session_id}_{timestamp}.png"
        canvas.save(final_path)

        print(f"\n✓ Final comic assembled: {final_path}")

        return str(final_path)
