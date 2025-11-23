"""Comic Assembly Agent - Combines panels into final comic strip."""
from PIL import Image, ImageDraw, ImageFont
from typing import List
from pathlib import Path
from datetime import datetime
from models import GeneratedPanel, ComicStrip, StoryPlan
from config import Config


class ComicAssemblerAgent:
    """Agent responsible for assembling final comic strip."""

    def __init__(self):
        """Initialize Comic Assembler Agent."""
        self.output_dir = Config.OUTPUT_DIR
        self.panel_spacing = Config.PANEL_SPACING
        self.border_width = Config.BORDER_WIDTH
        self.background_color = (255, 255, 255)  # White
        self.border_color = (0, 0, 0)  # Black

    def assemble_comic(
        self,
        story_plan: StoryPlan,
        generated_panels: List[GeneratedPanel],
        session_id: str,
        add_title: bool = True
    ) -> ComicStrip:
        """Assemble panels into final comic strip.

        Args:
            story_plan: Original story plan
            generated_panels: List of generated panels with images
            session_id: Session identifier
            add_title: Whether to add title at top

        Returns:
            ComicStrip: Complete comic strip with final image
        """
        print("Assembling final comic strip...")

        # Load all panel images
        panel_images = []
        for panel in generated_panels:
            img = Image.open(panel.image_path)
            panel_images.append(img)

        # Calculate dimensions
        dimensions = self._calculate_canvas_dimensions(
            panel_images,
            add_title
        )

        # Create canvas
        canvas = Image.new(
            'RGB',
            (dimensions['width'], dimensions['height']),
            self.background_color
        )

        # Add title if requested
        y_offset = self.panel_spacing
        if add_title:
            y_offset = self._add_title(canvas, story_plan.title)

        # Arrange panels horizontally
        x_offset = self.panel_spacing

        for img in panel_images:
            # Resize panel to standard size if needed
            resized_panel = self._resize_panel(img)

            # Add border
            bordered_panel = self._add_border(resized_panel)

            # Paste onto canvas
            canvas.paste(bordered_panel, (x_offset, y_offset))

            # Move to next position
            x_offset += bordered_panel.width + self.panel_spacing

        # Save final comic
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comic_{session_id}_{timestamp}.png"
        output_path = self.output_dir / filename
        canvas.save(output_path)

        print(f"✓ Comic strip saved to: {output_path}")

        # Create ComicStrip object
        comic_strip = ComicStrip(
            story_plan=story_plan,
            panels=generated_panels,
            final_image_path=str(output_path),
            generation_metadata={
                "session_id": session_id,
                "timestamp": timestamp,
                "num_panels": len(generated_panels),
                "title_included": add_title
            }
        )

        return comic_strip

    def _calculate_canvas_dimensions(
        self,
        panel_images: List[Image.Image],
        add_title: bool
    ) -> dict:
        """Calculate canvas dimensions for comic strip.

        Args:
            panel_images: List of panel images
            add_title: Whether title will be added

        Returns:
            Dict with width and height
        """
        # Standard panel dimensions
        panel_width = Config.PANEL_WIDTH
        panel_height = Config.PANEL_HEIGHT

        # Calculate total width
        num_panels = len(panel_images)
        total_width = (
            (panel_width + 2 * self.border_width) * num_panels +
            self.panel_spacing * (num_panels + 1)
        )

        # Calculate height
        title_height = 80 if add_title else 0
        total_height = (
            panel_height +
            2 * self.border_width +
            2 * self.panel_spacing +
            title_height
        )

        return {
            'width': total_width,
            'height': total_height
        }

    def _resize_panel(self, image: Image.Image) -> Image.Image:
        """Resize panel to standard dimensions.

        Args:
            image: Panel image

        Returns:
            Resized image
        """
        target_size = (Config.PANEL_WIDTH, Config.PANEL_HEIGHT)

        # Resize maintaining aspect ratio
        image.thumbnail(target_size, Image.Resampling.LANCZOS)

        # Create new image with exact dimensions (add padding if needed)
        resized = Image.new('RGB', target_size, self.background_color)

        # Center the image
        x_offset = (target_size[0] - image.width) // 2
        y_offset = (target_size[1] - image.height) // 2
        resized.paste(image, (x_offset, y_offset))

        return resized

    def _add_border(self, image: Image.Image) -> Image.Image:
        """Add border around panel.

        Args:
            image: Panel image

        Returns:
            Image with border
        """
        bordered = Image.new(
            'RGB',
            (
                image.width + 2 * self.border_width,
                image.height + 2 * self.border_width
            ),
            self.border_color
        )

        bordered.paste(image, (self.border_width, self.border_width))

        return bordered

    def _add_title(self, canvas: Image.Image, title: str) -> int:
        """Add title to top of canvas.

        Args:
            canvas: Canvas image
            title: Comic title

        Returns:
            Y offset for panel placement (below title)
        """
        draw = ImageDraw.Draw(canvas)

        # Try to load a nice font
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                32
            )
        except:
            font = ImageFont.load_default()

        # Get text size
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center title
        x = (canvas.width - text_width) // 2
        y = self.panel_spacing

        # Draw title
        draw.text((x, y), title, fill=self.border_color, font=font)

        # Return y offset for panels
        return y + text_height + self.panel_spacing

    def export_individual_panels(
        self,
        generated_panels: List[GeneratedPanel],
        session_id: str
    ) -> List[str]:
        """Export individual panels as separate files.

        Args:
            generated_panels: List of generated panels
            session_id: Session identifier

        Returns:
            List of output file paths
        """
        output_paths = []

        for panel in generated_panels:
            # Load image
            img = Image.open(panel.image_path)

            # Add border
            bordered = self._add_border(img)

            # Save
            filename = f"{session_id}_final_panel_{panel.panel.number}.png"
            output_path = self.output_dir / filename
            bordered.save(output_path)

            output_paths.append(str(output_path))

        print(f"✓ Exported {len(output_paths)} individual panels")
        return output_paths

    def create_pdf(
        self,
        comic_strip: ComicStrip,
        session_id: str
    ) -> str:
        """Create PDF version of comic strip.

        Args:
            comic_strip: Complete comic strip
            session_id: Session identifier

        Returns:
            Path to PDF file
        """
        if not comic_strip.final_image_path:
            raise ValueError("Comic strip has no final image")

        # Load image
        image = Image.open(comic_strip.final_image_path)

        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Save as PDF
        pdf_filename = f"comic_{session_id}.pdf"
        pdf_path = self.output_dir / pdf_filename
        image.save(pdf_path, 'PDF', resolution=100.0)

        print(f"✓ PDF saved to: {pdf_path}")
        return str(pdf_path)
