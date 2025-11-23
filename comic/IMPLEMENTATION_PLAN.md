# Comic Strip Generator - Implementation Plan

## Project Setup

### Prerequisites
- Python 3.10+
- Google Cloud account with Gemini API access
- API key for Gemini

### Installation Steps

1. **Install dependencies**:
```bash
pip install google-genai google-adk pillow python-dotenv
```

2. **Configure API credentials**:
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

## Implementation Phases

### Phase 1: Project Structure Setup ✓
- [x] Create `comic/` directory
- [ ] Create subdirectories: `agents/`, `tools/`, `output/`
- [ ] Set up `requirements.txt`
- [ ] Create `.env` template
- [ ] Create configuration file

### Phase 2: Character Library & Tools
- [ ] Implement `character_library.json` with default Calvin & Hobbes-style characters
- [ ] Create `imagen_tool.py` for Gemini API wrapper
- [ ] Create `image_editor_tool.py` for text overlay and composition

### Phase 3: Core Agents Implementation
- [ ] **Story Planning Agent** (`story_planner.py`)
  - Parse user prompts
  - Generate 3-4 panel story structure
  - Kid-friendly content filtering
  - Output structured story beats

- [ ] **Character Consistency Manager** (`character_manager.py`)
  - Load character library
  - Generate detailed visual descriptions
  - Create prompt templates with character details
  - Manage character state across panels

- [ ] **Scene Description Agent** (`scene_describer.py`)
  - Combine story + characters + style
  - Generate detailed Imagen prompts
  - Ensure Calvin & Hobbes aesthetic
  - Maintain scene continuity

- [ ] **Image Generation Agent** (`image_generator.py`)
  - Initialize Gemini chat session
  - Generate images sequentially for consistency
  - Handle API errors and retries
  - Save images with metadata

- [ ] **Dialogue & Text Agent** (`dialogue_agent.py`)
  - Extract dialogue from story plan
  - Position speech bubbles
  - Add text overlays to images
  - Format panel numbers

- [ ] **Comic Assembly Agent** (`comic_assembler.py`)
  - Arrange panels horizontally
  - Add borders and spacing
  - Create final composite
  - Export multiple formats

### Phase 4: Orchestration Layer
- [ ] Implement main orchestrator (`orchestrator.py`)
  - Define agent workflow sequence
  - Handle inter-agent communication
  - Manage state and error handling
  - Coordinate parallel operations where possible

### Phase 5: CLI and Integration
- [ ] Create `main.py` with CLI interface
- [ ] Add example usage and documentation
- [ ] Implement logging and debugging
- [ ] Add progress indicators

### Phase 6: Testing & Refinement
- [ ] Test with sample prompts
- [ ] Validate character consistency
- [ ] Refine prompts for better style matching
- [ ] Optimize image generation parameters
- [ ] Add error handling and edge cases

## File Structure

```
comic/
├── agents/
│   ├── __init__.py
│   ├── story_planner.py          # Story planning LLM agent
│   ├── character_manager.py      # Character consistency manager
│   ├── scene_describer.py        # Scene description agent
│   ├── image_generator.py        # Image generation agent
│   ├── dialogue_agent.py         # Dialogue & text overlay agent
│   └── comic_assembler.py        # Comic assembly agent
├── tools/
│   ├── __init__.py
│   ├── imagen_tool.py            # Gemini Imagen API wrapper
│   └── image_editor_tool.py     # PIL-based image editing tools
├── output/                        # Generated comics output directory
├── character_library.json        # Character definitions
├── config.py                     # Configuration management
├── orchestrator.py               # Main workflow orchestrator
├── main.py                       # CLI entry point
├── requirements.txt              # Python dependencies
├── .env.template                 # Environment variables template
├── ARCHITECTURE.md               # Architecture documentation
├── IMPLEMENTATION_PLAN.md        # This file
└── README.md                     # User documentation
```

## Key Implementation Details

### 1. Story Planning Agent
```python
# Uses ADK LLM Agent with structured output
agent = LLMAgent(
    name="StoryPlanner",
    model="gemini-2.0-flash",
    system_prompt="""You are a story planner for kid-friendly comic strips
    in Calvin and Hobbes style. Create 3-4 panel stories that are:
    - Wholesome and age-appropriate
    - Humorous with clever wordplay
    - Feature imaginative scenarios
    - Have satisfying punchlines
    """,
    output_schema=StoryPlan
)
```

### 2. Character Consistency Strategy
```python
# Maintain consistent character descriptions in every prompt
character_template = """
{name}: {age} year old {description}.
Wearing: {clothing}.
Hair: {hair_description}.
Expression: {expression}.
Style: Black and white line art, Calvin and Hobbes style,
       simple features, expressive face.
"""
```

### 3. Multi-turn Image Generation
```python
# Use single chat session for all panels to maintain consistency
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

# Generate panels sequentially
for panel in panels:
    prompt = build_detailed_prompt(panel, characters, style_guide)
    response = chat.send_message(prompt)
    save_panel_image(response, panel.number)
```

### 4. Comic Assembly
```python
# Use PIL to create final composite
from PIL import Image, ImageDraw, ImageFont

def assemble_comic(panel_images, dialogues):
    # Calculate dimensions
    panel_width = 800
    panel_height = 450
    spacing = 20
    border = 10

    # Create canvas
    num_panels = len(panel_images)
    canvas_width = (panel_width + spacing) * num_panels + spacing
    canvas_height = panel_height + 2 * spacing

    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')

    # Paste panels
    for i, panel_img in enumerate(panel_images):
        x_pos = spacing + i * (panel_width + spacing)
        canvas.paste(panel_img, (x_pos, spacing))

    # Add dialogue overlays
    add_speech_bubbles(canvas, dialogues)

    return canvas
```

## Testing Strategy

### Test Cases

1. **Simple Scenario**: "A kid and tiger playing in the backyard"
2. **Imaginative Scenario**: "A kid imagines being a space explorer"
3. **Dialogue-Heavy**: "Kid and tiger having a philosophical conversation"
4. **Action Sequence**: "Kid building a snowman with unexpected results"

### Validation Criteria

- ✅ Characters look consistent across all panels
- ✅ Story has clear beginning, middle, and end
- ✅ Dialogue is kid-friendly and humorous
- ✅ Art style matches Calvin & Hobbes aesthetic
- ✅ Panels are properly arranged and readable
- ✅ Speech bubbles are positioned correctly

## Configuration Parameters

### `.env` Template
```bash
# API Configuration
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3-pro-image-preview

# Generation Settings
IMAGE_SIZE=2K
ASPECT_RATIO=16:9
NUM_PANELS=4

# Style Settings
ART_STYLE="Calvin and Hobbes"
COLOR_MODE=black_and_white
```

### `config.py`
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Settings
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-3-pro-image-preview')

    # Image Settings
    IMAGE_SIZE = os.getenv('IMAGE_SIZE', '2K')
    ASPECT_RATIO = os.getenv('ASPECT_RATIO', '16:9')
    PANEL_WIDTH = 800
    PANEL_HEIGHT = 450

    # Comic Settings
    NUM_PANELS = int(os.getenv('NUM_PANELS', 4))
    PANEL_SPACING = 20
    BORDER_WIDTH = 10

    # Style Settings
    ART_STYLE = os.getenv('ART_STYLE', 'Calvin and Hobbes')
    COLOR_MODE = os.getenv('COLOR_MODE', 'black_and_white')

    # Output Settings
    OUTPUT_DIR = 'output'
    OUTPUT_FORMAT = 'PNG'
```

## Usage Example

```bash
# Run the comic generator
python main.py "Create a comic about a kid who thinks doing homework will give him superpowers"

# Expected output:
# → Planning story...
# → Loading characters...
# → Generating panel descriptions...
# → Creating panel 1/4...
# → Creating panel 2/4...
# → Creating panel 3/4...
# → Creating panel 4/4...
# → Adding dialogue...
# → Assembling final comic...
# ✓ Comic saved to: output/comic_20250123_143022.png
```

## Next Steps

After implementation:
1. Create comprehensive README with examples
2. Add sample outputs to showcase capabilities
3. Implement web interface (optional)
4. Add support for custom characters
5. Enable multi-page comics
6. Add animation export (GIF format)
