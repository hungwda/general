#!/usr/bin/env python3
"""Comic Strip Generator - Main Entry Point using Google ADK."""
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from google.adk.runners import Runner

# Import the root agent
from comic_agents import root_agent
from image_generation_tool import ImageGenerationTool


def main():
    """Main entry point for comic strip generator."""
    parser = argparse.ArgumentParser(
        description="Generate kid-friendly comic strips in Calvin and Hobbes style using Google ADK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "A kid tries to avoid homework by building a time machine"
  %(prog)s "A tiger and kid debate about breakfast cereal"
  %(prog)s "A kid discovers their stuffed animal can talk"
        """
    )

    parser.add_argument(
        'prompt',
        help='Story idea or theme for the comic strip'
    )

    parser.add_argument(
        '--api-key',
        help='Google API key (or set GOOGLE_API_KEY env var)'
    )

    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory for generated comics (default: output)'
    )

    parser.add_argument(
        '--session-id',
        help='Custom session ID (default: auto-generated timestamp)'
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("Error: GOOGLE_API_KEY not set", file=sys.stderr)
        print("Please set it via environment variable or --api-key argument", file=sys.stderr)
        return 1

    # Generate session ID
    session_id = args.session_id or datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*70)
    print("COMIC STRIP GENERATOR - Google ADK")
    print("="*70)
    print(f"\nPrompt: {args.prompt}")
    print(f"Session ID: {session_id}")
    print(f"Output: {output_dir}")
    print("\n" + "="*70 + "\n")

    try:
        # Initialize the ADK runner
        print("→ Initializing Google ADK Runner...")
        runner = Runner(
            agent=root_agent,
            api_key=api_key,
        )

        # Run the agent workflow
        print("→ Running comic generation workflow...\n")
        result = runner.run(user_prompt=args.prompt)

        print("\n" + "-"*70)
        print("Workflow Complete!")
        print("-"*70 + "\n")

        # Extract results from state
        state = result.state if hasattr(result, 'state') else {}

        # Save intermediate results
        results_file = output_dir / f"{session_id}_workflow_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "session_id": session_id,
                "prompt": args.prompt,
                "story_plan": state.get('story_plan'),
                "scene_prompts": state.get('scene_prompts'),
                "generated_images": state.get('generated_images'),
            }, f, indent=2)

        print(f"✓ Workflow results saved to: {results_file}\n")

        # Now generate actual images using the scene prompts
        print("→ Generating panel images...\n")

        scene_prompts_data = state.get('scene_prompts')
        story_plan_data = state.get('story_plan')

        if scene_prompts_data and story_plan_data:
            # Parse if string
            if isinstance(scene_prompts_data, str):
                # Extract JSON from markdown code blocks if present
                if "```json" in scene_prompts_data:
                    scene_prompts_data = scene_prompts_data.split("```json")[1].split("```")[0].strip()
                elif "```" in scene_prompts_data:
                    scene_prompts_data = scene_prompts_data.split("```")[1].split("```")[0].strip()
                scene_prompts_data = json.loads(scene_prompts_data)

            if isinstance(story_plan_data, str):
                if "```json" in story_plan_data:
                    story_plan_data = story_plan_data.split("```json")[1].split("```")[0].strip()
                elif "```" in story_plan_data:
                    story_plan_data = story_plan_data.split("```")[1].split("```")[0].strip()
                story_plan_data = json.loads(story_plan_data)

            # Initialize image generation tool
            img_tool = ImageGenerationTool(api_key=api_key, output_dir=str(output_dir))

            # Generate images
            generation_result = img_tool.generate_panel_images(
                scene_prompts=scene_prompts_data,
                session_id=session_id
            )

            # Assemble final comic
            print("\n→ Assembling final comic strip...\n")
            final_comic_path = img_tool.assemble_comic(
                generated_panels=generation_result['generated_panels'],
                story_plan=story_plan_data,
                session_id=session_id
            )

            print("\n" + "="*70)
            print("GENERATION COMPLETE!")
            print("="*70)
            print(f"\nTitle: {story_plan_data.get('title', 'Comic Strip')}")
            print(f"Panels: {generation_result['successful']}/{generation_result['total_panels']}")
            print(f"\nFinal Comic: {final_comic_path}")
            print(f"Workflow Data: {results_file}")
            print("\n")

        else:
            print("Warning: Could not extract scene prompts or story plan from workflow")
            print("Check the workflow results file for details")

        return 0

    except KeyboardInterrupt:
        print("\n\nGeneration interrupted by user.", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
