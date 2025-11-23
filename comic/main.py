#!/usr/bin/env python3
"""Comic Strip Generator - CLI Entry Point."""
import argparse
import sys
from pathlib import Path

from orchestrator import ComicStripOrchestrator
from config import Config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate kid-friendly comic strips in Calvin and Hobbes style",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "A kid tries to avoid homework by building a time machine"
  %(prog)s "A tiger and kid have a philosophical debate about breakfast cereal" --pdf
  %(prog)s --preview "A kid discovers their stuffed animal can talk"
        """
    )

    parser.add_argument(
        'prompt',
        help='Story idea or theme for the comic strip'
    )

    parser.add_argument(
        '--no-title',
        action='store_true',
        help='Do not add title to final comic'
    )

    parser.add_argument(
        '--pdf',
        action='store_true',
        help='Also export comic as PDF'
    )

    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview story plan without generating images'
    )

    parser.add_argument(
        '--api-key',
        help='Google API key (or set GOOGLE_API_KEY env var)'
    )

    parser.add_argument(
        '--output-dir',
        help='Output directory for generated comics'
    )

    args = parser.parse_args()

    # Handle output directory override
    if args.output_dir:
        Config.OUTPUT_DIR = Path(args.output_dir)
        Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Initialize orchestrator
        orchestrator = ComicStripOrchestrator(api_key=args.api_key)

        # Preview mode
        if args.preview:
            print("\nGenerating story preview...\n")
            summary = orchestrator.get_story_plan_summary(args.prompt)
            print(summary)
            print("\nTo generate the full comic with images, run without --preview flag.")
            return 0

        # Generate comic
        comic_strip = orchestrator.generate_comic(
            user_prompt=args.prompt,
            add_title=not args.no_title,
            export_pdf=args.pdf
        )

        return 0

    except ValueError as e:
        print(f"\nError: {e}", file=sys.stderr)
        print("\nPlease ensure you have set GOOGLE_API_KEY in your .env file", file=sys.stderr)
        print("or pass it via --api-key argument.", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\n\nGeneration interrupted by user.", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
