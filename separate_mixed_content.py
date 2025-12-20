#!/usr/bin/env python3
"""
LaTeX Persian/English Content Separator

This tool processes LaTeX files that contain mixed Persian and English text.
It separates paragraphs so that each line contains predominantly one language,
making the content more readable in editors.
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple


def has_persian(text: str) -> bool:
    """Check if text contains Persian characters."""
    # Persian Unicode range: \u0600-\u06FF (Arabic and Persian)
    persian_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(persian_pattern.search(text))


def has_english(text: str) -> bool:
    """Check if text contains English alphabetic characters."""
    # Match English letters
    english_pattern = re.compile(r'[a-zA-Z]')
    return bool(english_pattern.search(text))


def is_latex_command(line: str) -> bool:
    """Check if a line is primarily a LaTeX command."""
    stripped = line.strip()
    return (stripped.startswith('\\') or 
            stripped.startswith('%') or 
            stripped.startswith('{') or 
            stripped.startswith('}') or
            stripped == '')


def get_language_type(text: str) -> str:
    """Determine the predominant language in text."""
    has_per = has_persian(text)
    has_eng = has_english(text)
    
    if has_per and has_eng:
        return 'mixed'
    elif has_per:
        return 'persian'
    elif has_eng:
        return 'english'
    else:
        return 'neutral'


def split_mixed_line(line: str) -> List[str]:
    """Split a line with mixed Persian/English content into separate lines."""
    if not line.strip():
        return [line]
    
    # Don't split LaTeX commands
    if is_latex_command(line):
        return [line]
    
    lang_type = get_language_type(line)
    if lang_type != 'mixed':
        return [line]
    
    # Split by spaces and group consecutive words of the same language
    words = line.split()
    if not words:
        return [line]
    
    result = []
    current_group = []
    current_lang = None
    
    for word in words:
        word_lang = get_language_type(word)
        
        # Skip neutral words (numbers, punctuation) - add to current group
        if word_lang == 'neutral':
            current_group.append(word)
            continue
        
        # If this is mixed word or language changed, finalize current group
        if word_lang == 'mixed':
            # Mixed word - try to split it
            if current_group:
                result.append(' '.join(current_group))
                current_group = []
            result.append(word)
            current_lang = None
        elif current_lang is None:
            # First language group
            current_lang = word_lang
            current_group.append(word)
        elif word_lang == current_lang:
            # Same language, add to current group
            current_group.append(word)
        else:
            # Language changed, finalize current group and start new one
            if current_group:
                result.append(' '.join(current_group))
            current_group = [word]
            current_lang = word_lang
    
    # Add remaining group
    if current_group:
        result.append(' '.join(current_group))
    
    return result if result else [line]


def process_paragraph(paragraph: List[str]) -> List[str]:
    """Process a paragraph to separate mixed content."""
    result = []
    
    for line in paragraph:
        # Check if line has mixed content
        if get_language_type(line) == 'mixed' and not is_latex_command(line):
            # Split the line
            split_lines = split_mixed_line(line)
            result.extend(split_lines)
        else:
            result.append(line)
    
    return result


def process_latex_file(content: str) -> str:
    """Process entire LaTeX file content."""
    lines = content.split('\n')
    result = []
    current_paragraph = []
    
    for line in lines:
        # Check if this is a paragraph boundary
        if line.strip() == '':
            # Process accumulated paragraph
            if current_paragraph:
                processed = process_paragraph(current_paragraph)
                result.extend(processed)
                current_paragraph = []
            result.append(line)
        else:
            current_paragraph.append(line)
    
    # Process any remaining paragraph
    if current_paragraph:
        processed = process_paragraph(current_paragraph)
        result.extend(processed)
    
    return '\n'.join(result)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Separate mixed Persian/English content in LaTeX files'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Input LaTeX file path'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path (default: input_file with _separated suffix)'
    )
    parser.add_argument(
        '-i', '--in-place',
        action='store_true',
        help='Modify the input file in place'
    )
    
    args = parser.parse_args()
    
    # Read input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process content
    processed_content = process_latex_file(content)
    
    # Determine output path
    if args.in_place:
        output_path = input_path
    elif args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_separated{input_path.suffix}"
    
    # Write output
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        print(f"Successfully processed file. Output written to: {output_path}")
    except Exception as e:
        print(f"Error writing file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
