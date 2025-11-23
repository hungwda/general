"""Dialogue & Text Agent - Adds speech bubbles and text to comic panels."""
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Dict
from pathlib import Path
from models import GeneratedPanel, Panel
from config import Config


class DialogueAgent:
    """Agent responsible for adding dialogue and text overlays to panels."""

    def __init__(self):
        """Initialize Dialogue Agent."""
        self.output_dir = Config.OUTPUT_DIR
        self.default_font_size = 24
        self.bubble_padding = 15
        self.bubble_color = (255, 255, 255)  # White
        self.text_color = (0, 0, 0)  # Black
        self.outline_color = (0, 0, 0)  # Black
        self.outline_width = 2

    def add_dialogue_to_panel(
        self,
        generated_panel: GeneratedPanel,
        session_id: str
    ) -> GeneratedPanel:
        """Add dialogue overlays to a panel image.

        Args:
            generated_panel: Panel with generated image
            session_id: Session identifier

        Returns:
            GeneratedPanel: Panel with dialogue added
        """
        if not generated_panel.panel.dialogue:
            # No dialogue to add
            return generated_panel

        # Load image
        image = Image.open(generated_panel.image_path)

        # Add speech bubbles
        image_with_dialogue = self._add_speech_bubbles(
            image,
            generated_panel.panel.dialogue,
            generated_panel.panel.characters
        )

        # Save modified image
        filename = f"{session_id}_panel_{generated_panel.panel.number}_dialogue.png"
        output_path = self.output_dir / filename
        image_with_dialogue.save(output_path)

        # Update panel info
        updated_panel = GeneratedPanel(
            panel=generated_panel.panel,
            image_path=str(output_path),
            prompt_used=generated_panel.prompt_used,
            metadata={
                **generated_panel.metadata,
                "dialogue_added": True,
                "original_image": generated_panel.image_path
            }
        )

        return updated_panel

    def _add_speech_bubbles(
        self,
        image: Image.Image,
        dialogue: List[Dict[str, str]],
        characters: List[str]
    ) -> Image.Image:
        """Add speech bubbles to image.

        Args:
            image: Base image
            dialogue: List of dialogue entries
            characters: List of characters in scene

        Returns:
            Image with speech bubbles
        """
        draw = ImageDraw.Draw(image)
        img_width, img_height = image.size

        # Try to load a nice font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", self.default_font_size)
        except:
            font = ImageFont.load_default()

        # Position bubbles based on number of dialogue entries
        positions = self._calculate_bubble_positions(
            img_width,
            img_height,
            len(dialogue),
            characters
        )

        # Draw each speech bubble
        for i, dialogue_entry in enumerate(dialogue):
            text = dialogue_entry.get('text', '')
            position = positions[i]

            # Wrap text for bubble
            wrapped_text = self._wrap_text(text, font, img_width // 3)

            # Calculate bubble size
            bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            bubble_width = text_width + 2 * self.bubble_padding
            bubble_height = text_height + 2 * self.bubble_padding

            # Position bubble
            x = position[0] - bubble_width // 2
            y = position[1] - bubble_height // 2

            # Ensure bubble stays within image bounds
            x = max(10, min(x, img_width - bubble_width - 10))
            y = max(10, min(y, img_height - bubble_height - 10))

            # Draw bubble (ellipse for speech bubble effect)
            bubble_bbox = [x, y, x + bubble_width, y + bubble_height]
            draw.ellipse(bubble_bbox, fill=self.bubble_color, outline=self.outline_color, width=self.outline_width)

            # Draw text
            text_x = x + self.bubble_padding
            text_y = y + self.bubble_padding
            draw.multiline_text(
                (text_x, text_y),
                wrapped_text,
                fill=self.text_color,
                font=font,
                align='center'
            )

        return image

    def _calculate_bubble_positions(
        self,
        width: int,
        height: int,
        num_bubbles: int,
        characters: List[str]
    ) -> List[Tuple[int, int]]:
        """Calculate positions for speech bubbles.

        Args:
            width: Image width
            height: Image height
            num_bubbles: Number of bubbles to position
            characters: List of characters (for positioning hints)

        Returns:
            List of (x, y) positions for bubbles
        """
        positions = []

        # Simple positioning strategy: top row for speech bubbles
        # Distribute horizontally based on number of characters
        bubble_y = height // 5  # Top portion of image

        if num_bubbles == 1:
            # Single bubble, center
            positions.append((width // 2, bubble_y))
        elif num_bubbles == 2:
            # Two bubbles, left and right
            positions.append((width // 3, bubble_y))
            positions.append((2 * width // 3, bubble_y))
        else:
            # Multiple bubbles, distribute evenly
            for i in range(num_bubbles):
                x = (width // (num_bubbles + 1)) * (i + 1)
                y = bubble_y + (i % 2) * 40  # Slight vertical offset for alternating
                positions.append((x, y))

        return positions

    def _wrap_text(self, text: str, font: ImageFont, max_width: int) -> str:
        """Wrap text to fit within maximum width.

        Args:
            text: Text to wrap
            font: Font to use
            max_width: Maximum width in pixels

        Returns:
            Wrapped text with newlines
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            line_text = ' '.join(current_line)

            # Check width using a temporary draw
            temp_image = Image.new('RGB', (1, 1))
            temp_draw = ImageDraw.Draw(temp_image)
            bbox = temp_draw.textbbox((0, 0), line_text, font=font)
            line_width = bbox[2] - bbox[0]

            if line_width > max_width:
                if len(current_line) == 1:
                    # Single word too long, keep it
                    lines.append(current_line.pop())
                else:
                    # Remove last word and start new line
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]

        # Add remaining words
        if current_line:
            lines.append(' '.join(current_line))

        return '\n'.join(lines)

    def add_dialogue_to_all_panels(
        self,
        generated_panels: List[GeneratedPanel],
        session_id: str
    ) -> List[GeneratedPanel]:
        """Add dialogue to all panels.

        Args:
            generated_panels: List of generated panels
            session_id: Session identifier

        Returns:
            List of panels with dialogue added
        """
        panels_with_dialogue = []

        for panel in generated_panels:
            panel_with_dialogue = self.add_dialogue_to_panel(panel, session_id)
            panels_with_dialogue.append(panel_with_dialogue)
            print(f"✓ Added dialogue to panel {panel.panel.number}")

        return panels_with_dialogue
