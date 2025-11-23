"""Main Orchestrator - Coordinates all agents to generate comic strips."""
import os
from typing import Optional
from datetime import datetime
from google import genai

from config import Config
from models import ComicStrip
from agents import (
    StoryPlannerAgent,
    CharacterManager,
    SceneDescriberAgent,
    ImageGeneratorAgent,
    DialogueAgent,
    ComicAssemblerAgent,
)


class ComicStripOrchestrator:
    """Main orchestrator coordinating all agents."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the orchestrator.

        Args:
            api_key: Google API key (optional, will use env var if not provided)
        """
        # Set API key
        if api_key:
            Config.GOOGLE_API_KEY = api_key

        # Validate configuration
        Config.validate()

        # Initialize Google GenAI client
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)

        # Initialize agents
        self.story_planner = StoryPlannerAgent(self.client)
        self.character_manager = CharacterManager()
        self.scene_describer = SceneDescriberAgent(self.character_manager)
        self.image_generator = ImageGeneratorAgent(self.client)
        self.dialogue_agent = DialogueAgent()
        self.comic_assembler = ComicAssemblerAgent()

        # Session management
        self.session_id = self._generate_session_id()

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate_comic(
        self,
        user_prompt: str,
        add_title: bool = True,
        export_pdf: bool = False
    ) -> ComicStrip:
        """Generate complete comic strip from user prompt.

        Args:
            user_prompt: User's story idea or theme
            add_title: Whether to add title to final comic
            export_pdf: Whether to export PDF version

        Returns:
            ComicStrip: Complete comic strip with all panels
        """
        print("\n" + "="*60)
        print("COMIC STRIP GENERATOR")
        print("="*60)
        print(f"\nPrompt: {user_prompt}\n")

        # Step 1: Plan the story
        print("→ Planning story...")
        story_plan = self.story_planner.plan_story(user_prompt)
        print(f"✓ Created {len(story_plan.panels)}-panel story: '{story_plan.title}'")
        print(f"  Summary: {story_plan.summary}")

        # Step 2: Load character definitions
        print("\n→ Loading character definitions...")
        # Characters are loaded on-demand by scene describer

        # Step 3: Generate scene descriptions
        print("\n→ Generating detailed scene descriptions...")
        image_prompts = self.scene_describer.create_prompts_for_story(
            story_plan.panels,
            self.character_manager
        )
        print(f"✓ Created {len(image_prompts)} detailed image prompts")

        # Step 4: Generate panel images
        print("\n→ Generating panel images...")
        print("  (This may take a few minutes...)")
        generated_panels = self.image_generator.generate_all_panels(
            story_plan.panels,
            image_prompts,
            self.session_id
        )
        print(f"✓ Generated {len(generated_panels)} panel images")

        # Step 5: Add dialogue to panels
        print("\n→ Adding dialogue to panels...")
        panels_with_dialogue = self.dialogue_agent.add_dialogue_to_all_panels(
            generated_panels,
            self.session_id
        )
        print(f"✓ Added dialogue to all panels")

        # Step 6: Assemble final comic
        print("\n→ Assembling final comic strip...")
        comic_strip = self.comic_assembler.assemble_comic(
            story_plan,
            panels_with_dialogue,
            self.session_id,
            add_title=add_title
        )

        # Step 7: Export PDF if requested
        if export_pdf:
            print("\n→ Exporting PDF...")
            pdf_path = self.comic_assembler.create_pdf(
                comic_strip,
                self.session_id
            )
            comic_strip.generation_metadata['pdf_path'] = pdf_path

        # Print summary
        print("\n" + "="*60)
        print("GENERATION COMPLETE!")
        print("="*60)
        print(f"\nFinal comic: {comic_strip.final_image_path}")
        if export_pdf:
            print(f"PDF version: {comic_strip.generation_metadata['pdf_path']}")
        print(f"\nTitle: {story_plan.title}")
        print(f"Panels: {len(story_plan.panels)}")
        print(f"Characters: {', '.join(story_plan.characters_needed)}")
        print("\n")

        return comic_strip

    def refine_comic(
        self,
        comic_strip: ComicStrip,
        feedback: str
    ) -> ComicStrip:
        """Refine an existing comic based on feedback.

        Args:
            comic_strip: Existing comic strip
            feedback: User feedback for refinement

        Returns:
            ComicStrip: Refined comic strip
        """
        print(f"\n→ Refining comic based on feedback: '{feedback}'")

        # Refine story if needed
        refined_story = self.story_planner.refine_story(
            comic_strip.story_plan,
            feedback
        )

        # Regenerate with refined story
        return self.generate_comic(refined_story.summary)

    def export_individual_panels(self, comic_strip: ComicStrip) -> list:
        """Export individual panels from a comic strip.

        Args:
            comic_strip: Comic strip to export panels from

        Returns:
            List of panel file paths
        """
        return self.comic_assembler.export_individual_panels(
            comic_strip.panels,
            self.session_id
        )

    def get_story_plan_summary(self, user_prompt: str) -> str:
        """Get a story plan without generating images (for preview).

        Args:
            user_prompt: User's story idea

        Returns:
            str: Summary of the planned story
        """
        story_plan = self.story_planner.plan_story(user_prompt)

        summary = f"Title: {story_plan.title}\n\n"
        summary += f"Summary: {story_plan.summary}\n\n"
        summary += f"Panels:\n"

        for panel in story_plan.panels:
            summary += f"\nPanel {panel.number}:\n"
            summary += f"  Scene: {panel.scene_description}\n"
            summary += f"  Characters: {', '.join(panel.characters)}\n"
            summary += f"  Action: {panel.action}\n"
            if panel.dialogue:
                summary += f"  Dialogue:\n"
                for d in panel.dialogue:
                    summary += f"    {d['character']}: \"{d['text']}\"\n"

        return summary
