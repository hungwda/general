"""Utility functions for Comic Strip Generator."""
from pathlib import Path


def load_instruction_from_file(filename: str) -> str:
    """Load instruction text from file.

    Args:
        filename: Name of instruction file in instructions/ directory

    Returns:
        str: Instruction text content
    """
    instruction_path = Path(__file__).parent / "instructions" / filename

    if not instruction_path.exists():
        raise FileNotFoundError(f"Instruction file not found: {instruction_path}")

    with open(instruction_path, 'r') as f:
        return f.read()
