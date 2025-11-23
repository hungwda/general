# Comic Strip Generator

An agentic system that creates kid-friendly comic strips in **Calvin and Hobbes** style using Google's ADK (Agent Development Kit) and Gemini's Imagen API.

## Features

- 🎨 Generates 3-4 panel comic strips from simple prompts
- 🤖 Multi-agent architecture for consistent character and scene generation
- 👥 Character consistency across all panels
- 💬 Automatic speech bubble generation
- 📖 Kid-friendly content with wholesome humor
- 📄 Export as PNG or PDF

## Architecture

The system uses **Google ADK (Agent Development Kit)** with a LoopAgent workflow:

### ADK Agents

1. **Story Planner Agent** (`LlmAgent`) - Transforms user prompts into structured comic narratives
   - Model: `gemini-2.0-flash-exp`
   - Output: Saves story plan to state with key `story_plan`

2. **Scene Description Agent** (`LlmAgent`) - Generates detailed image prompts
   - Model: `gemini-2.0-flash-exp`
   - Reads: `story_plan` from state
   - Output: Saves scene prompts to state with key `scene_prompts`

3. **Image Coordinator Agent** (`LlmAgent`) - Coordinates image generation
   - Model: `gemini-2.0-flash-exp`
   - Reads: `scene_prompts` from state
   - Output: Saves generation info with key `generated_images`

### Workflow Orchestration

```python
comic_workflow_agent = LoopAgent(
    name="comic_strip_generator",
    sub_agents=[
        story_planner_agent,
        scene_describer_agent,
        image_coordinator_agent,
    ],
)
```

The LoopAgent executes agents sequentially, passing state between them. After the workflow completes, actual images are generated using Gemini's Imagen API and assembled into the final comic strip.

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## Installation

### Prerequisites

- Python 3.10 or higher
- Google Cloud account with Gemini API access
- Google API key

### Setup

1. **Clone or navigate to the repository**:
```bash
cd comic
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure API credentials**:
```bash
cp .env.template .env
# Edit .env and add your GOOGLE_API_KEY
```

Or export directly:
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

## Usage

### Basic Usage

Generate a comic from a prompt:

```bash
python main.py "A kid tries to avoid homework by building a time machine"
```

### With Options

```bash
# Generate comic and export as PDF
python main.py "A tiger and kid debate about breakfast cereal" --pdf

# Preview story plan without generating images
python main.py "A kid discovers their stuffed animal can talk" --preview

# Generate without title
python main.py "Adventures in the backyard" --no-title

# Specify custom output directory
python main.py "Space exploration adventure" --output-dir ./my_comics
```

### Using as a Library

```python
from google.adk.runners import Runner
from comic_agents import root_agent
from image_generation_tool import ImageGenerationTool

# Initialize runner
runner = Runner(
    agent=root_agent,
    api_key="your-api-key"
)

# Run workflow
result = runner.run(user_prompt="A kid builds a cardboard spaceship")

# Extract results
state = result.state
story_plan = state.get('story_plan')
scene_prompts = state.get('scene_prompts')

# Generate actual images
img_tool = ImageGenerationTool(api_key="your-api-key")
generation_result = img_tool.generate_panel_images(scene_prompts, "session_id")
final_comic = img_tool.assemble_comic(generation_result['generated_panels'], story_plan, "session_id")
```

## Example Prompts

Here are some example prompts to try:

- "A kid imagines being a superhero during math class"
- "A stuffed tiger gives life advice to a worried kid"
- "Building the world's biggest snowman goes hilariously wrong"
- "A kid tries to teach their pet tiger quantum physics"
- "An epic backyard adventure turns into a philosophical discussion"
- "A kid's invention to get out of chores backfires spectacularly"

## Configuration

Edit `.env` or `config.py` to customize:

- **Image Settings**: Size, aspect ratio, panel dimensions
- **Comic Settings**: Number of panels, spacing, borders
- **Style Settings**: Art style, color mode
- **API Settings**: Model selection, safety settings

## Output

Generated comics are saved to the `output/` directory with timestamps:

```
output/
├── comic_20250123_143022_20250123_143525.png  # Final comic
├── 20250123_143022_panel_1.png                # Individual panels
├── 20250123_143022_panel_2.png
├── ...
└── comic_20250123_143022.pdf                  # PDF version (if --pdf used)
```

## Character Library

The system includes default Calvin & Hobbes-style characters:

- **Max (Kid)**: Curious 6-year-old protagonist
- **Stripes (Companion)**: Wise stuffed tiger
- **Mom**: Patient, loving parent
- **Dad**: Logical, teaching-focused parent

Characters are defined in `character_library.json` and can be customized.

## Consistency Features

The system ensures consistency through:

1. **Multi-turn Chat**: Uses single chat session for all panels
2. **Detailed Descriptions**: Exhaustive character details in every prompt
3. **Character Templates**: Reusable character descriptions
4. **Scene Continuity**: Maintains setting across panels
5. **Style Anchors**: Consistent art style references

## Troubleshooting

### "GOOGLE_API_KEY not set" Error

Make sure you've set your API key:
```bash
export GOOGLE_API_KEY="your-key-here"
```

Or create a `.env` file with:
```
GOOGLE_API_KEY=your-key-here
```

### Image Generation Fails

- Check your API quota and billing
- Ensure you're using a model that supports image generation (gemini-2.0-flash-exp)
- Try reducing image size in config.py

### Characters Don't Look Consistent

- The system uses multi-turn chat for consistency, but variation is normal
- Try running again - each generation is unique
- Adjust character descriptions in `character_library.json` for more control

## Development

### Project Structure

```
comic/
├── instructions/              # Agent instruction files
│   ├── story_planner_instruction.txt
│   ├── scene_describer_instruction.txt
│   └── image_coordinator_instruction.txt
├── output/                    # Generated comics
├── comic_agents.py            # ADK agent definitions (LlmAgent, LoopAgent)
├── image_generation_tool.py   # Gemini Imagen API wrapper
├── util.py                    # Utility functions
├── main.py                    # CLI entry point with ADK Runner
├── character_library.json     # Character definitions
└── requirements.txt           # Dependencies
```

### Running Tests

```bash
# Preview mode to test story generation without images
python main.py "Test prompt" --preview

# Generate a test comic
python main.py "Quick test comic" --no-title
```

## API Costs

Image generation uses Google's Gemini API which may incur costs:

- Each comic generates 3-4 images (one per panel)
- Check current Gemini API pricing at https://ai.google.dev/pricing
- Use `--preview` mode to test story generation without image costs

## Future Enhancements

- [ ] Custom character upload and training
- [ ] Multiple art style support
- [ ] Multi-page comic generation
- [ ] Interactive panel editing
- [ ] Animation export (GIF format)
- [ ] Web interface

## Contributing

This project uses Google ADK for agent orchestration and Gemini Imagen API for image generation. Contributions welcome!

## License

MIT License - See LICENSE file for details

## Credits

- Built with [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- Image generation by [Gemini Imagen API](https://ai.google.dev/gemini-api/docs/image-generation)
- Inspired by Bill Watterson's **Calvin and Hobbes**

## Disclaimer

This project is a fan creation inspired by Calvin and Hobbes. It is not affiliated with or endorsed by Bill Watterson or Universal Uclick. Calvin and Hobbes is a registered trademark of Universal Uclick.
