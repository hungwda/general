"""Scene Description Agent - Generates detailed prompts for image generation."""
from typing import List
from models import Panel, Character, ImagePrompt
from agents.character_manager import CharacterManager
from config import Config


class SceneDescriberAgent:
    """Agent responsible for creating detailed image generation prompts."""

    def __init__(self, character_manager: CharacterManager):
        """Initialize Scene Describer Agent.

        Args:
            character_manager: CharacterManager instance for character details
        """
        self.character_manager = character_manager
        self.style_guide = character_manager.get_style_guide()

    def create_panel_prompt(
        self,
        panel: Panel,
        characters: List[Character],
        panel_type: str = "dialogue_panel"
    ) -> ImagePrompt:
        """Create detailed image generation prompt for a panel.

        Args:
            panel: Panel data with scene information
            characters: List of Character objects in the scene
            panel_type: Type of panel for template selection

        Returns:
            ImagePrompt: Detailed prompt for image generation
        """
        # Get base template
        template = self.character_manager.get_prompt_template(panel_type)

        # Build character description
        character_desc = self.character_manager.build_character_prompt_section(characters)

        # Get setting description
        setting_desc = self._enhance_setting(panel.setting)

        # Build composition notes
        composition = self._determine_composition(panel, len(characters))

        # Assemble full prompt
        full_prompt = self._assemble_prompt(
            template=template,
            character_description=character_desc,
            action=panel.action,
            setting=setting_desc,
            composition=composition,
            mood=panel.mood
        )

        # Extract style keywords
        style_keywords = self._extract_style_keywords()

        return ImagePrompt(
            panel_number=panel.number,
            full_prompt=full_prompt,
            characters_in_scene=characters,
            setting=panel.setting,
            composition_notes=composition,
            style_keywords=style_keywords
        )

    def _enhance_setting(self, setting: str) -> str:
        """Enhance setting description with style-appropriate details.

        Args:
            setting: Basic setting description

        Returns:
            str: Enhanced setting description
        """
        # Try to match to template
        setting_lower = setting.lower()
        for template_key in ['bedroom', 'backyard', 'kitchen', 'school', 'outdoor']:
            if template_key in setting_lower:
                return self.character_manager.get_scene_template(template_key)

        # Default enhancement
        return f"{setting}. {self.style_guide.get('backgrounds', 'Simple minimal background')}"

    def _determine_composition(self, panel: Panel, num_characters: int) -> str:
        """Determine composition notes based on panel content.

        Args:
            panel: Panel information
            num_characters: Number of characters in scene

        Returns:
            str: Composition guidelines
        """
        compositions = []

        # Panel format
        compositions.append("Wide horizontal comic panel format")

        # Character positioning
        if num_characters == 1:
            compositions.append("character centered or slightly off-center")
        elif num_characters == 2:
            compositions.append("characters facing each other in conversation")
        else:
            compositions.append("characters arranged across panel for balance")

        # Action-based composition
        if "run" in panel.action.lower() or "jump" in panel.action.lower():
            compositions.append("dynamic diagonal composition with motion lines")
        elif "sit" in panel.action.lower() or "stand" in panel.action.lower():
            compositions.append("stable horizontal composition")
        elif "look" in panel.action.lower() or "think" in panel.action.lower():
            compositions.append("close-up or medium shot emphasizing expression")

        # Dialogue composition
        if panel.dialogue:
            compositions.append("clear space above characters for speech bubbles")

        return ". ".join(compositions)

    def _assemble_prompt(
        self,
        template: str,
        character_description: str,
        action: str,
        setting: str,
        composition: str,
        mood: str
    ) -> str:
        """Assemble the complete prompt from components.

        Args:
            template: Base prompt template
            character_description: Character visual details
            action: What characters are doing
            setting: Scene setting
            composition: Composition guidelines
            mood: Emotional tone

        Returns:
            str: Complete assembled prompt
        """
        # Fill in template
        prompt = template.format(
            character_description=character_description,
            action=action,
            setting=setting,
            setting_detail=setting,
            composition_note=composition,
            expression=mood,
            action_description=action,
            motion_details="",
            pose=action
        )

        # Add style emphasis
        style_emphasis = (
            f" Art style: {self.style_guide.get('art_style', 'Calvin and Hobbes')}. "
            f"{self.style_guide.get('color_palette', 'Black and white line art')}. "
            f"{self.style_guide.get('character_emphasis', 'Expressive characters')}."
        )

        full_prompt = f"{prompt} {style_emphasis}"

        # Clean up extra spaces
        full_prompt = " ".join(full_prompt.split())

        return full_prompt

    def _extract_style_keywords(self) -> List[str]:
        """Extract key style keywords for consistency.

        Returns:
            List[str]: Style keywords
        """
        keywords = [
            "Calvin and Hobbes style",
            "black and white",
            "line art",
            "comic strip",
            "expressive",
            "minimal background",
            "hand-drawn",
            "kid-friendly"
        ]

        return keywords

    def create_prompts_for_story(
        self,
        panels: List[Panel],
        character_manager: CharacterManager
    ) -> List[ImagePrompt]:
        """Create prompts for all panels in a story.

        Args:
            panels: List of panels in story
            character_manager: CharacterManager for character details

        Returns:
            List[ImagePrompt]: Prompts for each panel
        """
        prompts = []

        for i, panel in enumerate(panels):
            # Determine panel type
            if i == 0:
                panel_type = "character_intro"
            elif i == len(panels) - 1:
                panel_type = "punchline_panel"
            else:
                panel_type = "dialogue_panel" if panel.dialogue else "action_panel"

            # Get characters with appropriate expressions
            expressions = {}
            for char_key in panel.characters:
                # Try to infer expression from dialogue or action
                expressions[char_key] = self._infer_expression(panel)

            characters = character_manager.get_characters_for_scene(
                panel.characters,
                expressions
            )

            # Create prompt
            prompt = self.create_panel_prompt(panel, characters, panel_type)
            prompts.append(prompt)

        return prompts

    def _infer_expression(self, panel: Panel) -> str:
        """Infer character expression from panel content.

        Args:
            panel: Panel information

        Returns:
            str: Inferred expression
        """
        action_lower = panel.action.lower()
        mood_lower = panel.mood.lower()

        # Check for expression keywords
        if any(word in action_lower for word in ["smile", "laugh", "grin"]):
            return "happy"
        elif any(word in action_lower for word in ["frown", "sad", "cry"]):
            return "sad"
        elif any(word in action_lower for word in ["surprise", "shock", "gasp"]):
            return "surprised"
        elif any(word in action_lower for word in ["angry", "mad", "frustrated"]):
            return "angry"
        elif any(word in action_lower for word in ["think", "wonder", "ponder"]):
            return "thoughtful"
        elif "excit" in mood_lower:
            return "excited"
        elif "mischiev" in mood_lower:
            return "mischievous"

        return "neutral"
