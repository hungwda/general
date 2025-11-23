"""Story Planning Agent - Transforms user prompts into structured comic narratives."""
import json
from typing import Dict, Any
from models import StoryPlan, Panel
from config import Config


class StoryPlannerAgent:
    """Agent responsible for planning comic strip stories."""

    def __init__(self, client):
        """Initialize the Story Planner Agent.

        Args:
            client: Google GenAI client instance
        """
        self.client = client
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build the system prompt for story planning."""
        return """You are an expert comic strip writer specializing in kid-friendly humor
in the style of Calvin and Hobbes. Your job is to transform user ideas into structured
comic strip stories.

Guidelines:
1. Create 3-4 panel comic strips (classic newspaper format)
2. Keep content wholesome and age-appropriate for kids 6-12 years
3. Use clever wordplay and imaginative scenarios
4. Include a clear setup, development, and punchline
5. Feature relatable childhood experiences with creative twists
6. Maintain the whimsical, philosophical tone of Calvin and Hobbes
7. Ensure each panel advances the story naturally

Story Structure:
- Panel 1: Setup - introduce situation and characters
- Panel 2: Development - escalate or complicate the scenario
- Panel 3: Continuation - build toward resolution
- Panel 4: Punchline - deliver satisfying conclusion with humor

Character Types Available:
- Kid (protagonist): Curious, imaginative 6-year-old
- Companion (stuffed tiger): Wise, sarcastic best friend
- Mom: Patient, loving, sometimes exasperated parent
- Dad: Logical, enjoys teaching moments, slightly sarcastic

Return your response as a JSON object matching this structure:
{
    "title": "Brief title for the comic",
    "summary": "One sentence summary",
    "panels": [
        {
            "number": 1,
            "scene_description": "What's happening in this panel",
            "characters": ["kid", "companion"],
            "dialogue": [{"character": "kid", "text": "What they say"}],
            "action": "What characters are doing",
            "setting": "Where this takes place",
            "mood": "emotional tone"
        }
    ],
    "characters_needed": ["kid", "companion"],
    "theme": "The main theme or moral",
    "target_age": "6-12 years"
}

Ensure dialogue is natural, witty, and kid-appropriate. Each panel should have a clear visual
that can be illustrated effectively."""

    def plan_story(self, user_prompt: str) -> StoryPlan:
        """Transform user prompt into structured story plan.

        Args:
            user_prompt: User's story idea or theme

        Returns:
            StoryPlan: Structured comic strip plan
        """
        # Build the full prompt
        full_prompt = f"""Create a kid-friendly comic strip based on this idea:

"{user_prompt}"

Remember to make it wholesome, humorous, and in the spirit of Calvin and Hobbes.
Include imaginative elements and clever dialogue. Return the complete story plan as JSON."""

        # Generate story plan using Gemini
        response = self.client.models.generate_content(
            model=Config.GEMINI_MODEL,
            contents=[
                {"role": "user", "parts": [{"text": self.system_prompt}]},
                {"role": "user", "parts": [{"text": full_prompt}]}
            ],
            config={
                "temperature": 0.9,  # Higher creativity for story generation
                "top_p": 0.95,
                "max_output_tokens": 2048,
            }
        )

        # Parse response
        response_text = response.text.strip()

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        # Parse JSON and validate
        try:
            story_data = json.loads(response_text)
            story_plan = StoryPlan(**story_data)
            return story_plan
        except Exception as e:
            raise ValueError(f"Failed to parse story plan: {e}\nResponse: {response_text}")

    def refine_story(self, story_plan: StoryPlan, feedback: str) -> StoryPlan:
        """Refine an existing story plan based on feedback.

        Args:
            story_plan: Current story plan
            feedback: User feedback or refinement request

        Returns:
            StoryPlan: Refined story plan
        """
        prompt = f"""Here's a comic strip story plan:

{story_plan.model_dump_json(indent=2)}

Please refine it based on this feedback: "{feedback}"

Return the complete updated story plan as JSON."""

        response = self.client.models.generate_content(
            model=Config.GEMINI_MODEL,
            contents=[
                {"role": "user", "parts": [{"text": self.system_prompt}]},
                {"role": "user", "parts": [{"text": prompt}]}
            ],
            config={
                "temperature": 0.8,
                "max_output_tokens": 2048,
            }
        )

        response_text = response.text.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()

        story_data = json.loads(response_text)
        return StoryPlan(**story_data)
