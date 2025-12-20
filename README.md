# Latex_Persian_Tools
A repository which contain tools for make latex file more readable and handy

## Tools

### 1. Mixed Content Separator (`separate_mixed_content.py`)

This tool processes LaTeX files that contain mixed Persian and English text. It automatically separates paragraphs so that each line contains predominantly one language, making the content more readable in editors.

#### Features
- Detects Persian and English text automatically
- Separates mixed-language paragraphs into single-language lines
- Preserves LaTeX commands and document structure
- Supports multiple output modes (new file, custom path, or in-place)

#### Usage

Basic usage (creates a new file with `_separated` suffix):
```bash
python3 separate_mixed_content.py input.tex
```

Specify custom output file:
```bash
python3 separate_mixed_content.py input.tex -o output.tex
```

Modify file in-place:
```bash
python3 separate_mixed_content.py input.tex -i
```

#### Example

**Input:**
```latex
این یک پاراگراف تستی است که شامل both Persian and English text می‌باشد.
```

**Output:**
```latex
این یک پاراگراف تستی است که شامل
both Persian and English text
می‌باشد.
```

#### Requirements
- Python 3.6+
- UTF-8 encoded LaTeX files

## Installation

Clone the repository:
```bash
git clone https://github.com/Ali-J-Fesharaki/Latex_Persian_Tools.git
cd Latex_Persian_Tools
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
