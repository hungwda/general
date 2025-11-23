# Comic Strip Generator - Agentic System Architecture

## Overview
A multi-agent system that generates kid-friendly comic strips in Calvin and Hobbes style from user prompts, using Google ADK for orchestration and Gemini Imagen API for image generation.

## System Architecture

### 1. **Story Planning Agent** (LLM Agent)
**Purpose**: Transform user prompt into a structured comic narrative

**Responsibilities**:
- Parse user input and extract story intent
- Generate 3-4 panel comic structure (classic Calvin & Hobbes format)
- Create panel-by-panel story beats with dialogue
- Ensure kid-friendly content filtering
- Maintain narrative coherence and humor style

**Output**: Structured story plan with panel descriptions

### 2. **Character Consistency Manager** (Workflow Agent)
**Purpose**: Maintain consistent character appearances across all panels

**Responsibilities**:
- Define and store character reference descriptions
- Create detailed visual descriptions (age, clothing, hair, expressions)
- Maintain character style guide (Calvin & Hobbes aesthetic)
- Generate character-specific prompt templates
- Ensure characters look identical across panels

**Character Library**:
```python
{
    "protagonist": {
        "base_description": "6-year-old boy, spiky blonde hair, red striped t-shirt,
                            blue jeans, mischievous expression",
        "style_notes": "Simple line art, expressive faces, minimal detail"
    },
    "companion": {
        "base_description": "stuffed tiger toy, orange with black stripes,
                            child-sized, animated and expressive",
        "style_notes": "Appears alive with personality, cartoonish features"
    }
}
```

### 3. **Scene Description Agent** (LLM Agent)
**Purpose**: Generate detailed Imagen prompts for each panel

**Responsibilities**:
- Combine story beats with character descriptions
- Add environmental details and composition
- Specify Calvin & Hobbes art style elements:
  - Black and white line art with minimal shading
  - Simple backgrounds with expressive characters
  - Wide horizontal panel format
  - Hand-drawn aesthetic
- Include dialogue placement notes
- Maintain visual continuity between panels

**Prompt Template**:
```
"Black and white comic strip panel in Calvin and Hobbes style.
[CHARACTER DESCRIPTION] in [SCENE SETTING].
[ACTION/POSE]. Simple line art, expressive faces, minimal background detail.
[COMPOSITION NOTES]. Hand-drawn aesthetic, kid-friendly."
```

### 4. **Image Generation Agent** (Tool-based Agent)
**Purpose**: Generate panel images using Gemini Imagen API

**Responsibilities**:
- Call Gemini API with optimized prompts
- Use multi-turn chat for panel-to-panel consistency
- Configure image parameters:
  - Aspect ratio: 16:9 (horizontal comic panel)
  - Image size: 2K for quality
  - Response modality: IMAGE
- Handle retries and error cases
- Save generated images with metadata

**API Implementation**:
```python
chat = client.chats.create(
    model="gemini-3-pro-image-preview",
    config=types.GenerateContentConfig(
        response_modalities=['IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K"
        )
    )
)

# Generate each panel in sequence for consistency
for panel_prompt in panel_prompts:
    response = chat.send_message(panel_prompt)
```

### 5. **Dialogue & Text Agent** (Workflow Agent)
**Purpose**: Add speech bubbles and text overlays

**Responsibilities**:
- Extract dialogue from story plan
- Position speech bubbles appropriately
- Use comic-appropriate font (Comic Sans or similar)
- Ensure text readability
- Add panel numbers if needed

### 6. **Comic Assembly Agent** (Workflow Agent)
**Purpose**: Combine panels into final comic strip

**Responsibilities**:
- Arrange panels in reading order (left-to-right)
- Add panel borders and spacing
- Create final composite image
- Add optional title/date
- Export in multiple formats (PNG, PDF)

**Output Layout**:
```
+------------------+------------------+------------------+
|     Panel 1      |     Panel 2      |     Panel 3      |
|   [Image + Text] | [Image + Text]   | [Image + Text]   |
+------------------+------------------+------------------+
```

### 7. **Orchestrator Agent** (Workflow Agent - Sequential)
**Purpose**: Coordinate all agents in proper sequence

**Workflow**:
```
User Prompt
    → Story Planning Agent
    → Character Consistency Manager (parallel character refs)
    → Scene Description Agent (for each panel)
    → Image Generation Agent (sequential for consistency)
    → Dialogue & Text Agent
    → Comic Assembly Agent
    → Final Output
```

## Consistency Strategies

### Character Consistency
1. **Reference Images**: Generate initial character reference in first panel
2. **Multi-turn Chat**: Use same chat session for all panels
3. **Detailed Descriptions**: Include exhaustive visual details in every prompt
4. **Style Anchors**: Consistently reference "Calvin and Hobbes style" aesthetic

### Scene Consistency
1. **Location Continuity**: Maintain setting descriptions across panels
2. **Lighting/Time**: Keep consistent time-of-day and lighting
3. **Visual Transitions**: Ensure smooth panel-to-panel flow

### Story Consistency
1. **Beat Tracking**: Maintain story state across panels
2. **Dialogue Flow**: Natural conversation progression
3. **Action Continuity**: Logical pose and action sequences

## Technical Stack

### Dependencies
```python
google-genai        # Gemini API client
google-adk          # Agent Development Kit
Pillow              # Image processing
python-dotenv       # Configuration management
```

### File Structure
```
comic/
├── agents/
│   ├── __init__.py
│   ├── story_planner.py
│   ├── character_manager.py
│   ├── scene_describer.py
│   ├── image_generator.py
│   ├── dialogue_agent.py
│   └── comic_assembler.py
├── tools/
│   ├── __init__.py
│   ├── imagen_tool.py
│   └── image_editor_tool.py
├── orchestrator.py
├── config.py
├── character_library.json
├── requirements.txt
└── main.py
```

## Safety & Content Filtering

### Kid-Friendly Filters
- Block inappropriate language/themes in story planning
- Filter violent or scary content
- Ensure positive, educational humor
- Maintain wholesome character interactions

### Gemini Safety Settings
```python
safety_settings = {
    "harassment": "BLOCK_MEDIUM_AND_ABOVE",
    "hate_speech": "BLOCK_MEDIUM_AND_ABOVE",
    "sexually_explicit": "BLOCK_LOW_AND_ABOVE",
    "dangerous_content": "BLOCK_MEDIUM_AND_ABOVE"
}
```

## Example Flow

**User Input**: "Create a comic about a kid trying to avoid homework by building a time machine"

**Story Planning Output**:
```
Panel 1: Kid at desk, homework in front, looks bored. Companion suggests time travel.
Panel 2: Kid building elaborate cardboard contraption with companion's "help"
Panel 3: Kid triumphantly presents "time machine" - a cardboard box with buttons
Panel 4: Mom appears asking "Is your homework done?" Kid and companion look sheepish
```

**Character Manager Output**:
```
Character A: "Young boy, 6 years old, spiky blonde hair pointing upward,
              red and black striped t-shirt, blue jeans, sneakers..."

Character B: "Stuffed tiger toy, orange fur with black stripes, round face,
              expressive eyes, child-sized, sitting/standing poses..."
```

**Scene Description Output (Panel 1)**:
```
"Black and white comic strip panel in Calvin and Hobbes style.
A 6-year-old boy with spiky blonde hair wearing a red striped t-shirt
sits at a wooden desk, chin resting on hand, looking bored at an open
math textbook. A stuffed tiger toy sits beside him with an animated,
mischievous expression. Simple line art, minimal shading, sparse
background detail showing bedroom. Wide horizontal composition.
Hand-drawn aesthetic, kid-friendly."
```

## Performance Considerations

- **Parallel Processing**: Generate character descriptions in parallel
- **Caching**: Store character references to avoid regeneration
- **Batching**: Process panels sequentially but optimize API calls
- **Error Handling**: Retry failed image generations with adjusted prompts

## Future Enhancements

1. **Custom Character Upload**: Allow users to provide character references
2. **Style Transfer**: Support different comic styles beyond Calvin & Hobbes
3. **Animation**: Generate simple panel-to-panel animations
4. **Interactive Editing**: Allow users to refine individual panels
5. **Multi-page Comics**: Extend to longer story formats
