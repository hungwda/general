"""Comic Strip Generator Agents using Google ADK."""
from google.adk.agents import LlmAgent, LoopAgent
from util import load_instruction_from_file


# --- Sub Agent 1: Story Planner ---
# Converts user prompt into structured comic story plan
story_planner_agent = LlmAgent(
    name="StoryPlanner",
    model="gemini-2.0-flash-exp",
    instruction=load_instruction_from_file("story_planner_instruction.txt"),
    description="Plans kid-friendly comic strip stories in Calvin and Hobbes style",
    output_key="story_plan",  # Save story plan to state
)


# --- Sub Agent 2: Scene Describer ---
# Creates detailed image generation prompts for each panel
scene_describer_agent = LlmAgent(
    name="SceneDescriber",
    model="gemini-2.0-flash-exp",
    instruction=load_instruction_from_file("scene_describer_instruction.txt"),
    description="Generates detailed image prompts with character consistency",
    output_key="scene_prompts",  # Save prompts to state
)


# --- Sub Agent 3: Image Coordinator ---
# Coordinates image generation for all panels
image_coordinator_agent = LlmAgent(
    name="ImageCoordinator",
    model="gemini-2.0-flash-exp",
    instruction=load_instruction_from_file("image_coordinator_instruction.txt"),
    description="Coordinates panel image generation",
    output_key="generated_images",  # Save generation info to state
)


# --- Loop Agent Workflow ---
# Executes agents in sequence: Plan → Describe → Generate
comic_workflow_agent = LoopAgent(
    name="comic_strip_generator",
    sub_agents=[
        story_planner_agent,
        scene_describer_agent,
        image_coordinator_agent,
    ],
)


# --- Root Agent for the Runner ---
root_agent = comic_workflow_agent
