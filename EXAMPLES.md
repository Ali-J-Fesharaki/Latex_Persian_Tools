# Example Usage Guide

## Basic Example

Suppose you have a LaTeX file `document.tex` with mixed Persian/English content:

```latex
\documentclass{article}
\usepackage{xepersian}

\begin{document}

The concept of machine learning یادگیری ماشین has evolved dramatically in recent years.

\end{document}
```

Run the tool:
```bash
python3 separate_mixed_paragraphs.py document.tex
```

The file will be modified in place to:
```latex
\documentclass{article}
\usepackage{xepersian}

\begin{document}

The concept of machine learning
یادگیری ماشین
has evolved dramatically in recent years.

\end{document}
```

## Advanced Usage

### Keep original file and create new output:
```bash
python3 separate_mixed_paragraphs.py input.tex -o output.tex
```

### Process only longer paragraphs (e.g., minimum 60 characters):
```bash
python3 separate_mixed_paragraphs.py document.tex -m 60
```

## Why Use This Tool?

Many text editors struggle to properly display bidirectional text (Persian + English) on the same line. This tool makes your LaTeX source more readable by separating mixed-language content into individual lines, where each line contains primarily one language.

### Benefits:
- **Better Readability**: Each line contains text in a single direction
- **Easier Editing**: Locate and modify text more easily
- **AI-Friendly**: When using AI tools to generate LaTeX, separated lines are easier to work with
- **Version Control**: Clearer diffs in git/svn when changes are made

## What Gets Processed?

The tool intelligently processes:
- ✅ Medium and long paragraphs (≥40 characters by default)
- ✅ Lines with both Persian and English text
- ✅ Content in list items (`\item`)
- ✅ Text with LaTeX inline commands (`\textbf`, `\emph`, etc.)

The tool preserves:
- ✅ LaTeX structure commands (`\section`, `\begin{}`, etc.)
- ✅ Comments
- ✅ Pure English paragraphs
- ✅ Pure Persian paragraphs  
- ✅ Short lines (below threshold)
- ✅ Indentation and formatting
