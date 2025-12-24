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
from typing import List


# Compile regex patterns at module level for better performance
PERSIAN_PATTERN = re.compile(r'[\u0600-\u06FF]')
ENGLISH_PATTERN = re.compile(r'[a-zA-Z]')
# Pattern for characters that should be grouped with English (ASCII symbols, numbers, etc.)
# Excludes basic punctuation like . , ; ! ? that can appear in both languages
ENGLISH_SYMBOLS_PATTERN = re.compile(r'[a-zA-Z0-9$()=[\]{}|<>+\-*/\\\'"`~@#%^&_]')
# Basic punctuation that can belong to either language context
PUNCTUATION_PATTERN = re.compile(r'[.,;:!?]')


def has_persian(text: str) -> bool:
    """Check if text contains Persian characters."""
    # Persian Unicode range: \u0600-\u06FF (Arabic and Persian)
    return bool(PERSIAN_PATTERN.search(text))


def has_english(text: str) -> bool:
    """Check if text contains English alphabetic characters."""
    # Match English letters
    return bool(ENGLISH_PATTERN.search(text))


def is_latex_command(line: str) -> bool:
    """Check if a line is primarily a LaTeX command."""
    stripped = line.strip()
    return (stripped.startswith('\\') or 
            stripped.startswith('%') or 
            stripped.startswith('{') or 
            stripped.startswith('}') or
            stripped == '')


def has_english_or_symbols(text: str) -> bool:
    """Check if text contains English characters or symbols that should be grouped with English."""
    return bool(ENGLISH_SYMBOLS_PATTERN.search(text))


def get_language_type(text: str) -> str:
    """Determine the predominant language in text."""
    has_per = has_persian(text)
    has_eng_or_sym = has_english_or_symbols(text)
    
    if has_per and has_eng_or_sym:
        return 'mixed'
    elif has_per:
        return 'persian'
    elif has_eng_or_sym:
        return 'english'
    else:
        return 'neutral'


def split_mixed_word(word: str) -> List[str]:
    """Split a word that contains both Persian and English/symbols into separate parts."""
    if not word:
        return []
    
    parts = []
    current_part = []
    current_type = None
    
    for char in word:
        if PERSIAN_PATTERN.search(char):
            char_type = 'persian'
        elif ENGLISH_SYMBOLS_PATTERN.search(char):
            char_type = 'english'
        elif PUNCTUATION_PATTERN.search(char):
            # Punctuation follows the current type context
            char_type = 'punctuation'
        else:
            char_type = 'neutral'
        
        # Punctuation follows the current language
        if char_type == 'punctuation':
            if current_type in ['persian', 'english']:
                current_part.append(char)
            else:
                # No context, treat as neutral
                if current_part:
                    parts.append(''.join(current_part))
                    current_part = []
                current_part.append(char)
                current_type = 'neutral'
        elif char_type == 'neutral' and current_type is not None:
            current_part.append(char)
        elif char_type == 'neutral':
            # Start a new neutral part
            if current_part:
                parts.append(''.join(current_part))
                current_part = []
            current_part.append(char)
            current_type = 'neutral'
        elif current_type is None or char_type == current_type:
            # Same type, add to current part
            current_part.append(char)
            current_type = char_type
        else:
            # Type changed, save current part and start new one
            if current_part:
                parts.append(''.join(current_part))
            current_part = [char]
            current_type = char_type
    
    # Add remaining part
    if current_part:
        parts.append(''.join(current_part))
    
    return parts if parts else [word]


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
        
        # If this is a mixed word, split it into parts
        if word_lang == 'mixed':
            # Save current group before processing mixed word
            if current_group:
                result.append(' '.join(current_group))
                current_group = []
                current_lang = None
            
            # Split the mixed word and process each part
            parts = split_mixed_word(word)
            for part in parts:
                part_lang = get_language_type(part)
                if part_lang == 'neutral':
                    # Attach neutral parts to current group if available
                    if current_group:
                        current_group.append(part)
                    else:
                        result.append(part)
                elif current_lang is None or part_lang == current_lang:
                    # Same language or first part
                    current_group.append(part)
                    current_lang = part_lang
                else:
                    # Language changed
                    if current_group:
                        result.append(' '.join(current_group))
                    current_group = [part]
                    current_lang = part_lang
        
        elif word_lang == 'neutral':
            # Attach neutral words to current group if available
            if current_lang is not None:
                current_group.append(word)
            else:
                # No current group, add as standalone
                result.append(word)
        
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
