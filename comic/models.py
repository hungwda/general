"""Data models for Comic Strip Generator."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Character(BaseModel):
    """Character definition."""
    name: str
    role: str  # 'protagonist', 'companion', 'supporting'
    description: str
    visual_details: str
    expression: str = "neutral"


class Panel(BaseModel):
    """Individual comic panel."""
    number: int
    scene_description: str
    characters: List[str]
    dialogue: List[Dict[str, str]] = Field(default_factory=list)  # [{"character": "name", "text": "..."}]
    action: str
    setting: str
    mood: str = "lighthearted"


class StoryPlan(BaseModel):
    """Complete story plan for comic strip."""
    title: str
    summary: str
    panels: List[Panel]
    characters_needed: List[str]
    theme: str
    target_age: str = "6-12 years"


class ImagePrompt(BaseModel):
    """Detailed prompt for image generation."""
    panel_number: int
    full_prompt: str
    characters_in_scene: List[Character]
    setting: str
    composition_notes: str
    style_keywords: List[str]


class GeneratedPanel(BaseModel):
    """Panel with generated image."""
    panel: Panel
    image_path: str
    prompt_used: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ComicStrip(BaseModel):
    """Complete comic strip output."""
    story_plan: StoryPlan
    panels: List[GeneratedPanel]
    final_image_path: Optional[str] = None
    generation_metadata: Dict[str, Any] = Field(default_factory=dict)
