"""Character Consistency Manager - Maintains consistent character appearances."""
import json
from typing import Dict, List
from pathlib import Path
from models import Character
from config import Config


class CharacterManager:
    """Manages character definitions and ensures consistency across panels."""

    def __init__(self):
        """Initialize Character Manager with character library."""
        self.library_path = Config.CHARACTER_LIBRARY_PATH
        self.character_library = self._load_library()
        self.active_characters: Dict[str, Character] = {}

    def _load_library(self) -> Dict:
        """Load character library from JSON file."""
        if not self.library_path.exists():
            raise FileNotFoundError(
                f"Character library not found at {self.library_path}"
            )

        with open(self.library_path, 'r') as f:
            return json.load(f)

    def get_character(self, character_key: str, expression: str = "neutral") -> Character:
        """Get character with specified expression.

        Args:
            character_key: Key in character library (e.g., 'kid', 'companion')
            expression: Desired expression for the character

        Returns:
            Character: Character object with full description
        """
        if character_key not in self.character_library['default_characters']:
            raise ValueError(f"Character '{character_key}' not found in library")

        char_data = self.character_library['default_characters'][character_key]

        # Build detailed visual description
        visual_details = self._build_visual_description(char_data, expression)

        character = Character(
            name=char_data['name'],
            role=character_key,
            description=char_data['base_description'],
            visual_details=visual_details,
            expression=expression
        )

        # Cache for consistency
        self.active_characters[character_key] = character
        return character

    def _build_visual_description(self, char_data: Dict, expression: str) -> str:
        """Build detailed visual description for consistent generation.

        Args:
            char_data: Character data from library
            expression: Desired expression

        Returns:
            str: Detailed visual description
        """
        parts = [
            char_data['base_description'],
            f"Wearing: {char_data['clothing']}" if 'clothing' in char_data else "",
            f"Hair: {char_data['hair']}" if 'hair' in char_data else "",
            f"Features: {char_data['features']}",
            f"Expression: {expression}",
            f"Style: {char_data['style_notes']}"
        ]

        return ". ".join(filter(None, parts))

    def get_characters_for_scene(
        self,
        character_keys: List[str],
        expressions: Dict[str, str] = None
    ) -> List[Character]:
        """Get multiple characters for a scene.

        Args:
            character_keys: List of character keys
            expressions: Optional dict mapping character keys to expressions

        Returns:
            List[Character]: List of character objects
        """
        expressions = expressions or {}
        characters = []

        for key in character_keys:
            expression = expressions.get(key, "neutral")
            character = self.get_character(key, expression)
            characters.append(character)

        return characters

    def build_character_prompt_section(self, characters: List[Character]) -> str:
        """Build the character section of an image generation prompt.

        Args:
            characters: List of characters in the scene

        Returns:
            str: Character description for prompt
        """
        if not characters:
            return ""

        if len(characters) == 1:
            return characters[0].visual_details

        # Multiple characters
        descriptions = []
        for char in characters:
            descriptions.append(
                f"{char.name} ({char.visual_details})"
            )

        return " and ".join(descriptions)

    def get_style_guide(self) -> Dict:
        """Get the overall style guide for comic generation.

        Returns:
            Dict: Style guide configuration
        """
        return self.character_library.get('style_guide', {})

    def get_scene_template(self, scene_type: str) -> str:
        """Get scene template description.

        Args:
            scene_type: Type of scene (e.g., 'bedroom', 'backyard')

        Returns:
            str: Scene description template
        """
        templates = self.character_library.get('scene_templates', {})
        return templates.get(scene_type, "Simple background with minimal detail")

    def get_prompt_template(self, template_type: str) -> str:
        """Get prompt template for specific panel type.

        Args:
            template_type: Type of template (e.g., 'character_intro', 'action_panel')

        Returns:
            str: Prompt template string
        """
        templates = self.character_library.get('prompt_templates', {})
        return templates.get(
            template_type,
            "Black and white comic strip panel in Calvin and Hobbes style. {character_description} {action}. Simple line art, minimal background."
        )
