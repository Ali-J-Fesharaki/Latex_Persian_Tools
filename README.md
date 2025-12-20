# Latex_Persian_Tools
A repository which contains tools to make LaTeX files more readable and handy, especially when working with mixed Persian and English content.

## Tools

### 1. Separate Mixed Paragraphs (`separate_mixed_paragraphs.py`)

This tool processes LaTeX files that contain mixed Persian and English text. It automatically separates lines with mixed languages into multiple lines, making the content more readable in text editors that struggle to display bidirectional text properly.

#### Features
- Detects paragraphs with mixed Persian/Arabic and English text
- Separates mixed-language lines into individual lines per language segment
- Preserves LaTeX structure and commands
- Handles medium and long paragraphs (configurable minimum length)
- Preserves indentation and formatting

#### Usage

Basic usage (overwrites input file):
```bash
python3 separate_mixed_paragraphs.py input.tex
```

Specify output file:
```bash
python3 separate_mixed_paragraphs.py input.tex -o output.tex
```

Adjust minimum line length threshold:
```bash
python3 separate_mixed_paragraphs.py input.tex -m 50
```

#### Example

**Before:**
```latex
This is a paragraph with both English and Persian text سلام دنیا which appears on the same line.
```

**After:**
```latex
This is a paragraph with both English and Persian text
سلام دنیا
which appears on the same line.
```

#### Command-line Options
- `input`: Input LaTeX (.tex) file path (required)
- `-o, --output`: Output file path (default: overwrites input file)
- `-m, --min-length`: Minimum line length to process (default: 40 characters)

#### Requirements
- Python 3.6+
- No external dependencies required

## Testing

Run the test suite to verify the tool works correctly:

```bash
python3 test_separator.py
```

The test suite includes:
- Character detection tests (Persian/English)
- Mixed language detection
- Line separation logic
- File processing
- Error handling

## Contributing

Contributions are welcome! Please ensure tests pass before submitting pull requests.
