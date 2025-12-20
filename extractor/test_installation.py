#!/usr/bin/env python3
"""
Test script to verify Medical Data Extractor installation and configuration.
"""

import sys
from pathlib import Path


def test_python_version():
    """Test Python version."""
    print("Testing Python version...", end=" ")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False


def test_imports():
    """Test required package imports."""
    print("\nTesting package imports:")

    packages = [
        ("ollama", "ollama"),
        ("PIL", "Pillow"),
        ("fitz", "PyMuPDF"),
        ("pathlib", "pathlib"),
        ("tqdm", "tqdm"),
    ]

    all_passed = True
    for module, package_name in packages:
        try:
            __import__(module)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} (not installed)")
            all_passed = False

    return all_passed


def test_ollama_connection():
    """Test Ollama connection."""
    print("\nTesting Ollama connection...", end=" ")

    try:
        import ollama
        # Try to list models
        models = ollama.list()
        print("✓ Connected to Ollama")
        return True
    except Exception as e:
        print(f"✗ Cannot connect to Ollama")
        print(f"  Error: {e}")
        print("  Make sure Ollama is running: ollama serve")
        return False


def test_ollama_models():
    """Test if vision models are available."""
    print("\nChecking for vision models:")

    try:
        import ollama
        models = ollama.list()

        model_names = [model['name'] for model in models.get('models', [])]

        vision_models = [name for name in model_names if 'llava' in name.lower()]

        if vision_models:
            for model in vision_models:
                print(f"  ✓ {model}")
            return True
        else:
            print("  ✗ No LLaVA vision models found")
            print("  Install with: ollama pull llava:latest")
            return False

    except Exception as e:
        print(f"  ✗ Error checking models: {e}")
        return False


def test_module_imports():
    """Test importing local modules."""
    print("\nTesting Medical Data Extractor modules:")

    modules = [
        "document_processor",
        "llm_extractor",
        "output_handler",
        "pipeline",
        "config",
    ]

    all_passed = True
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ✗ {module}")
            print(f"    Error: {e}")
            all_passed = False

    return all_passed


def test_output_directory():
    """Test output directory creation."""
    print("\nTesting output directory creation...", end=" ")

    try:
        from output_handler import OutputHandler
        handler = OutputHandler(output_dir="test_output")
        print("✓ Output handler initialized")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("="*60)
    print("Medical Data Extractor - Installation Test")
    print("="*60)

    tests = [
        test_python_version,
        test_imports,
        test_ollama_connection,
        test_ollama_models,
        test_module_imports,
        test_output_directory,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with error: {e}")
            results.append(False)

    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✓ All tests passed! Installation is complete.")
        print("\nYou can now use the Medical Data Extractor:")
        print("  python main.py --help")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("  1. Install missing packages: pip install -r requirements.txt")
        print("  2. Install Ollama: https://ollama.ai")
        print("  3. Start Ollama: ollama serve")
        print("  4. Install vision model: ollama pull llava:latest")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
