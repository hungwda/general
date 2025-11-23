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

The system uses a **multi-agent architecture** with specialized agents:

1. **Story Planner Agent** - Transforms user prompts into structured comic narratives
2. **Character Consistency Manager** - Maintains consistent character appearances
3. **Scene Description Agent** - Generates detailed image prompts
4. **Image Generation Agent** - Creates panels using Gemini Imagen API
5. **Dialogue Agent** - Adds speech bubbles and text overlays
6. **Comic Assembler Agent** - Combines panels into final comic strip

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
from orchestrator import ComicStripOrchestrator

# Initialize orchestrator
orchestrator = ComicStripOrchestrator(api_key="your-api-key")

# Generate comic
comic = orchestrator.generate_comic(
    user_prompt="A kid builds a cardboard spaceship",
    add_title=True,
    export_pdf=True
)

# Access results
print(f"Comic saved to: {comic.final_image_path}")
print(f"Story: {comic.story_plan.summary}")
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
├── agents/                    # Agent implementations
│   ├── story_planner.py
│   ├── character_manager.py
│   ├── scene_describer.py
│   ├── image_generator.py
│   ├── dialogue_agent.py
│   └── comic_assembler.py
├── tools/                     # Helper tools
├── output/                    # Generated comics
├── character_library.json     # Character definitions
├── config.py                  # Configuration
├── models.py                  # Data models
├── orchestrator.py            # Main orchestrator
├── main.py                    # CLI entry point
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
