#!/usr/bin/env python3
"""
LaTeX Persian/English Paragraph Separator

This tool processes LaTeX files containing mixed Persian and English text,
separating mixed-language lines into multiple lines for better readability
in text editors.
"""

import argparse
import re
import sys
from pathlib import Path


def is_persian_char(char):
    """Check if a character is Persian/Arabic."""
    code_point = ord(char)
    # Persian/Arabic Unicode ranges:
    # Arabic: 0x0600-0x06FF
    # Arabic Supplement: 0x0750-0x077F
    # Arabic Extended-A: 0x08A0-0x08FF
    # Arabic Presentation Forms-A: 0xFB50-0xFDFF
    # Arabic Presentation Forms-B: 0xFE70-0xFEFF
    return (
        (0x0600 <= code_point <= 0x06FF) or
        (0x0750 <= code_point <= 0x077F) or
        (0x08A0 <= code_point <= 0x08FF) or
        (0xFB50 <= code_point <= 0xFDFF) or
        (0xFE70 <= code_point <= 0xFEFF)
    )


def is_english_char(char):
    """Check if a character is English/Latin."""
    code_point = ord(char)
    # Basic Latin: 0x0000-0x007F
    # Latin-1 Supplement: 0x0080-0x00FF
    # Latin Extended-A: 0x0100-0x017F
    # Latin Extended-B: 0x0180-0x024F
    return (
        (0x0041 <= code_point <= 0x005A) or  # A-Z
        (0x0061 <= code_point <= 0x007A) or  # a-z
        (0x0080 <= code_point <= 0x00FF) or
        (0x0100 <= code_point <= 0x017F) or
        (0x0180 <= code_point <= 0x024F)
    )


def analyze_line_languages(line):
    """
    Analyze a line and determine which parts are Persian vs English.
    Returns a list of tuples: (text_segment, language) where language is 'persian', 'english', or 'other'
    """
    if not line.strip():
        return [(line, 'empty')]
    
    segments = []
    current_segment = []
    current_lang = None
    
    for char in line:
        char_lang = None
        if is_persian_char(char):
            char_lang = 'persian'
        elif is_english_char(char):
            char_lang = 'english'
        else:
            # Whitespace, punctuation, numbers, etc. - keep with current segment
            char_lang = 'other'
        
        # If we have a language switch (and it's not just punctuation/whitespace)
        if char_lang in ['persian', 'english']:
            if current_lang is None:
                current_lang = char_lang
            elif current_lang != char_lang:
                # Language switch - save current segment and start new one
                if current_segment:
                    segments.append((''.join(current_segment), current_lang))
                current_segment = [char]
                current_lang = char_lang
                continue
        
        current_segment.append(char)
    
    # Add the last segment
    if current_segment:
        if current_lang is None:
            current_lang = 'other'
        segments.append((''.join(current_segment), current_lang))
    
    return segments


def has_mixed_languages(line):
    """Check if a line contains both Persian and English text."""
    has_persian = any(is_persian_char(c) for c in line)
    has_english = any(is_english_char(c) for c in line)
    return has_persian and has_english


def is_latex_command_line(line):
    """Check if line is primarily a LaTeX command (structural, not content)."""
    stripped = line.strip()
    
    # Lines that are just closing/opening braces or empty
    if stripped in ['{', '}', '']:
        return True
    
    # Comment lines
    if stripped.startswith('%'):
        return True
    
    # Structural LaTeX commands (not content-bearing ones like \item, \textbf, etc.)
    structural_commands = [
        '\\documentclass', '\\usepackage', '\\begin{', '\\end{',
        '\\section', '\\subsection', '\\subsubsection',
        '\\chapter', '\\part', '\\paragraph',
        '\\maketitle', '\\tableofcontents',
        '\\newcommand', '\\renewcommand', '\\def',
        '\\label', '\\ref', '\\cite', '\\bibliography'
    ]
    
    for cmd in structural_commands:
        if stripped.startswith(cmd):
            return True
    
    return False


def separate_mixed_line(line, indent_level=0):
    """
    Separate a line with mixed languages into multiple lines.
    Each language segment gets its own line, preserving indentation.
    """
    segments = analyze_line_languages(line)
    
    # Get original indentation
    original_indent = len(line) - len(line.lstrip())
    indent = ' ' * original_indent
    
    # Filter out segments that are just whitespace or very short
    meaningful_segments = []
    for text, lang in segments:
        # Skip segments that are just whitespace
        if text.strip():
            meaningful_segments.append((text.strip(), lang))
    
    # If only one meaningful segment, no need to separate
    if len(meaningful_segments) <= 1:
        return [line]
    
    # Check if we actually have mixed languages
    langs = set(lang for _, lang in meaningful_segments if lang in ['persian', 'english'])
    if len(langs) < 2:
        return [line]
    
    # Create separated lines
    separated_lines = []
    for text, lang in meaningful_segments:
        separated_lines.append(indent + text + '\n')
    
    return separated_lines


def is_paragraph_line(line, context_lines=None):
    """
    Determine if a line is part of a text paragraph (not a command, not too short).
    Medium to long paragraphs are the target.
    """
    stripped = line.strip()
    
    # Skip empty lines
    if not stripped:
        return False
    
    # Skip LaTeX commands and special lines
    if is_latex_command_line(line):
        return False
    
    # Consider lines with substantial text (medium to long)
    # Minimum length threshold for processing
    if len(stripped) < 40:  # Short lines are not processed
        return False
    
    return True


def process_tex_file(input_path, output_path=None, min_length=40):
    """
    Process a LaTeX file, separating mixed-language lines.
    
    Args:
        input_path: Path to input .tex file
        output_path: Path to output .tex file (if None, overwrites input)
        min_length: Minimum line length to consider for processing
    """
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"Error: File {input_path} not found.", file=sys.stderr)
        return False
    
    # Read the file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Process lines
    processed_lines = []
    modifications_count = 0
    
    for i, line in enumerate(lines):
        # Check if this is a paragraph line that should be processed
        if is_paragraph_line(line) and has_mixed_languages(line):
            # Separate the mixed-language line
            separated = separate_mixed_line(line)
            if len(separated) > 1:
                processed_lines.extend(separated)
                modifications_count += 1
            else:
                processed_lines.append(line)
        else:
            processed_lines.append(line)
    
    # Write output
    if output_path is None:
        output_path = input_file
    
    output_file = Path(output_path)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(processed_lines)
    
    print(f"Processed {input_path}")
    print(f"Modified {modifications_count} lines with mixed languages")
    print(f"Output written to {output_path}")
    
    return True


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Separate mixed Persian/English lines in LaTeX files for better readability.'
    )
    parser.add_argument(
        'input',
        help='Input LaTeX (.tex) file path'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: overwrites input file)',
        default=None
    )
    parser.add_argument(
        '-m', '--min-length',
        type=int,
        default=40,
        help='Minimum line length to process (default: 40)'
    )
    
    args = parser.parse_args()
    
    success = process_tex_file(args.input, args.output, args.min_length)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
