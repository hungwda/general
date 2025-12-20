#!/usr/bin/env python3
"""
Standalone PII redaction utility.
Can be used to redact existing markdown files without re-extracting.
"""

import argparse
import sys
from pathlib import Path

from pii_redactor import PIIRedactor


def main():
    """Main entry point for standalone redaction."""

    parser = argparse.ArgumentParser(
        description='Redact PII from markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Redact a single file:
    python redact_standalone.py --file document.md

  Redact all files in a directory:
    python redact_standalone.py --directory ./output

  Redact with custom marker:
    python redact_standalone.py --file doc.md --marker "[###]"

  Redact only specific PII types:
    python redact_standalone.py --file doc.md --include names dob

  Exclude specific PII types:
    python redact_standalone.py --file doc.md --exclude contact

  Save redaction log:
    python redact_standalone.py --file doc.md --log redactions.json
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--file', '-f',
        type=str,
        help='Path to markdown file to redact'
    )
    input_group.add_argument(
        '--directory', '-d',
        type=str,
        help='Path to directory containing markdown files'
    )

    # Redaction options
    parser.add_argument(
        '--marker', '-m',
        type=str,
        default='[REDACTED]',
        help='Redaction marker text (default: [REDACTED])'
    )

    parser.add_argument(
        '--include',
        nargs='+',
        choices=['names', 'dob', 'ids', 'contact', 'age_over_89'],
        help='Only redact specific PII types'
    )

    parser.add_argument(
        '--exclude',
        nargs='+',
        choices=['names', 'dob', 'ids', 'contact', 'age_over_89'],
        help='Exclude specific PII types from redaction'
    )

    # Output options
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file/directory (default: overwrite in place)'
    )

    parser.add_argument(
        '--log',
        type=str,
        help='Save redaction log to file (JSON format)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be redacted without making changes'
    )

    args = parser.parse_args()

    # Initialize redactor
    redactor = PIIRedactor(
        redaction_marker=args.marker,
        preserve_structure=True,
        log_redactions=True
    )

    # Convert include/exclude to sets
    include_set = set(args.include) if args.include else None
    exclude_set = set(args.exclude) if args.exclude else None

    try:
        if args.file:
            # Single file redaction
            file_path = Path(args.file)

            if not file_path.exists():
                print(f"Error: File not found: {file_path}")
                return 1

            print(f"\nRedacting PII from: {file_path.name}")

            if args.dry_run:
                # Read and redact without saving
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                redacted_content = redactor.redact_all(
                    content,
                    include=include_set,
                    exclude=exclude_set
                )

                print(f"\nDry run complete - no files modified")
                print(f"Would redact {len(redactor.redaction_log)} PII items")

            else:
                output_path = Path(args.output) if args.output else None

                output_path, count = redactor.redact_file(
                    file_path,
                    output_path,
                    include=include_set,
                    exclude=exclude_set
                )

                print(f"\nRedaction complete!")
                print(f"Redacted {count} PII items")
                print(f"Output saved to: {output_path}")

            # Show summary
            summary = redactor.get_redaction_summary()
            if summary['by_type']:
                print("\nRedactions by type:")
                for pii_type, count in sorted(summary['by_type'].items()):
                    print(f"  - {pii_type}: {count}")

            # Save log if requested
            if args.log:
                redactor.save_redaction_log(Path(args.log))

            return 0

        elif args.directory:
            # Directory batch redaction
            directory = Path(args.directory)

            if not directory.exists() or not directory.is_dir():
                print(f"Error: Invalid directory: {directory}")
                return 1

            print(f"\nRedacting PII from all markdown files in: {directory}")

            if args.dry_run:
                print("\nDry run mode - no files will be modified")

                md_files = list(directory.glob('*.md'))
                md_files = [f for f in md_files if f.name not in ['README.md', 'INSTALL.md']]

                print(f"Would process {len(md_files)} files")
                return 0

            output_dir = Path(args.output) if args.output else None

            results = redactor.redact_directory(
                directory,
                output_dir,
                include=include_set,
                exclude=exclude_set
            )

            total_redactions = sum(count for _, count in results.values() if count)

            print(f"\nBatch redaction complete!")
            print(f"Processed {len(results)} files")
            print(f"Total redactions: {total_redactions}")

            # Save log if requested
            if args.log:
                redactor.save_redaction_log(Path(args.log))

            return 0

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
