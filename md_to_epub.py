#!/usr/bin/env python3
"""
Markdown to EPUB Converter
Converts a Markdown file to EPUB format using ebooklib and markdown libraries.
"""

import markdown
from ebooklib import epub
import re
import sys
from pathlib import Path


def convert_md_to_epub(md_path: str, output_path: str = None, title: str = None):
    """Convert a Markdown file to EPUB format."""

    md_file = Path(md_path)
    if not md_file.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    md_converter = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
    html_content = md_converter.convert(md_content)

    # Create EPUB book
    book = epub.EpubBook()

    # Set metadata
    book_title = title or md_file.stem.replace('-', ' ').replace('_', ' ').title()
    book.set_identifier(f'id-{md_file.stem}')
    book.set_title(book_title)
    book.set_language('en')
    book.add_author('Claude Skills Community')

    # Add CSS for styling
    style = '''
    body {
        font-family: Georgia, serif;
        line-height: 1.6;
        padding: 1em;
    }
    h1, h2, h3, h4 {
        color: #333;
        margin-top: 1.5em;
    }
    h1 { font-size: 2em; text-align: center; }
    h2 { font-size: 1.5em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }
    h3 { font-size: 1.2em; }
    code {
        background-color: #f4f4f4;
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-family: monospace;
    }
    pre {
        background-color: #f4f4f4;
        padding: 1em;
        overflow-x: auto;
        border-radius: 5px;
    }
    pre code {
        background: none;
        padding: 0;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #f4f4f4;
    }
    a {
        color: #0066cc;
    }
    ul, ol {
        padding-left: 2em;
    }
    li {
        margin: 0.3em 0;
    }
    blockquote {
        border-left: 4px solid #ccc;
        margin: 1em 0;
        padding-left: 1em;
        color: #666;
    }
    img {
        max-width: 100%;
        height: auto;
    }
    '''

    css = epub.EpubItem(
        uid="style",
        file_name="style/main.css",
        media_type="text/css",
        content=style
    )
    book.add_item(css)

    # Create main chapter
    chapter = epub.EpubHtml(title=book_title, file_name='content.xhtml', lang='en')
    chapter.content = f'''
    <html>
    <head>
        <title>{book_title}</title>
        <link rel="stylesheet" type="text/css" href="style/main.css"/>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    '''
    chapter.add_item(css)
    book.add_item(chapter)

    # Add navigation
    book.toc = [epub.Link('content.xhtml', book_title, 'content')]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Set spine
    book.spine = ['nav', chapter]

    # Generate output path
    if output_path is None:
        output_path = md_file.with_suffix('.epub')

    # Write EPUB file
    epub.write_epub(str(output_path), book, {})

    return output_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python md_to_epub.py <input.md> [output.epub] [title]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    title = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        result = convert_md_to_epub(input_file, output_file, title)
        print(f"Successfully converted to: {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
