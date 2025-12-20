#!/usr/bin/env python3
"""
Unit tests for separate_mixed_paragraphs.py

Run with: python3 test_separator.py
"""

import sys
import tempfile
from pathlib import Path

# Import the module
import separate_mixed_paragraphs as smp


def test_is_persian_char():
    """Test Persian character detection."""
    assert smp.is_persian_char('س'), "Should detect Persian character"
    assert smp.is_persian_char('ا'), "Should detect Persian character"
    assert not smp.is_persian_char('a'), "Should not detect English as Persian"
    assert not smp.is_persian_char('1'), "Should not detect digit as Persian"
    print("✓ test_is_persian_char passed")


def test_is_english_char():
    """Test English character detection."""
    assert smp.is_english_char('a'), "Should detect English character"
    assert smp.is_english_char('Z'), "Should detect English character"
    assert not smp.is_english_char('س'), "Should not detect Persian as English"
    assert not smp.is_english_char('1'), "Should not detect digit as English"
    print("✓ test_is_english_char passed")


def test_has_mixed_languages():
    """Test mixed language detection."""
    assert smp.has_mixed_languages("Hello سلام"), "Should detect mixed content"
    assert smp.has_mixed_languages("Test فارسی mixed"), "Should detect mixed content"
    assert not smp.has_mixed_languages("Pure English text"), "Should not detect pure English as mixed"
    assert not smp.has_mixed_languages("متن فارسی خالص"), "Should not detect pure Persian as mixed"
    print("✓ test_has_mixed_languages passed")


def test_is_latex_command_line():
    """Test LaTeX command line detection."""
    assert smp.is_latex_command_line("\\documentclass{article}"), "Should detect documentclass"
    assert smp.is_latex_command_line("\\section{Title}"), "Should detect section"
    assert smp.is_latex_command_line("% Comment"), "Should detect comment"
    assert not smp.is_latex_command_line("\\item Some content"), "Should not detect item as structural"
    assert not smp.is_latex_command_line("Regular text"), "Should not detect regular text"
    print("✓ test_is_latex_command_line passed")


def test_is_paragraph_line():
    """Test paragraph line detection."""
    long_line = "This is a long enough line with sufficient content to be processed"
    short_line = "Short"
    
    assert smp.is_paragraph_line(long_line, min_length=40), "Should detect long paragraph"
    assert not smp.is_paragraph_line(short_line, min_length=40), "Should not detect short line"
    assert not smp.is_paragraph_line("\\section{Title}", min_length=40), "Should not detect section"
    assert not smp.is_paragraph_line("", min_length=40), "Should not detect empty line"
    print("✓ test_is_paragraph_line passed")


def test_separate_mixed_line():
    """Test line separation."""
    mixed = "English text فارسی متن more English"
    result = smp.separate_mixed_line(mixed)
    
    assert len(result) > 1, "Should separate mixed line into multiple lines"
    assert any("English" in line for line in result), "Should contain English parts"
    assert any("فارسی" in line for line in result), "Should contain Persian parts"
    
    # Pure language should not be separated
    pure_english = "This is pure English text"
    result_pure = smp.separate_mixed_line(pure_english)
    assert len(result_pure) == 1, "Should not separate pure language line"
    
    print("✓ test_separate_mixed_line passed")


def test_process_tex_file():
    """Test file processing."""
    # Create a temporary test file
    test_content = """\\documentclass{article}

\\begin{document}

This is a medium length line with both English and Persian فارسی content here.

Pure English paragraph that should not be modified at all.

\\end{document}
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        temp_path = f.name
    
    try:
        # Process the file
        output_path = temp_path + ".out"
        success = smp.process_tex_file(temp_path, output_path)
        
        assert success, "Processing should succeed"
        assert Path(output_path).exists(), "Output file should be created"
        
        # Read and verify output
        with open(output_path, 'r', encoding='utf-8') as f:
            output = f.read()
        
        # Should have separated the mixed line
        assert "English and Persian" in output, "Should contain English part"
        assert "فارسی" in output, "Should contain Persian part"
        
        # Should preserve pure English
        assert "Pure English paragraph that should not be modified at all." in output
        
        print("✓ test_process_tex_file passed")
        
        # Cleanup
        Path(output_path).unlink()
        
    finally:
        Path(temp_path).unlink()


def test_nonexistent_file():
    """Test error handling for nonexistent file."""
    result = smp.process_tex_file("nonexistent_file.tex")
    assert not result, "Should return False for nonexistent file"
    print("✓ test_nonexistent_file passed")


def run_all_tests():
    """Run all tests."""
    print("Running tests for separate_mixed_paragraphs.py\n")
    
    try:
        test_is_persian_char()
        test_is_english_char()
        test_has_mixed_languages()
        test_is_latex_command_line()
        test_is_paragraph_line()
        test_separate_mixed_line()
        test_process_tex_file()
        test_nonexistent_file()
        
        print("\n" + "="*50)
        print("All tests passed! ✓")
        print("="*50)
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
