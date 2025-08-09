#!/usr/bin/env python3
"""
generate_post.py

Usage:
    python generate_post.py <markdown_file.md> <output.html>

This script converts a markdown file to HTML content suitable for insertion
inside a <div class="content"> element, preserving LaTeX formatting.
"""

import sys
import re
import yaml
import markdown
from pathlib import Path
import os

def parse_markdown(path):
    """Parse markdown file, extracting YAML front matter and markdown content."""
    text = open(path, 'r', encoding='utf-8').read()
    # Split YAML front-matter
    fm_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    m = re.match(fm_pattern, text, flags=re.S)
    if m:
        fm = yaml.safe_load(m.group(1))
        body_md = m.group(2)
    else:
        fm = {}
        body_md = text

    # **Sanitize**: remove any literal stray </p> lines in the markdown
    body_md = re.sub(r'(?m)^\s*</p>\s*$', '', body_md)

    return fm, body_md

def convert_markdown_to_html(markdown_content):
    """Convert markdown content to HTML, preserving LaTeX blocks."""
    # Preserve LaTeX blocks before markdown conversion
    # Save display math blocks ($$...$$)
    display_math_blocks = []
    def save_display_math(match):
        display_math_blocks.append(match.group(1))
        return f"DISPLAYMATH{len(display_math_blocks)-1}PLACEHOLDER"
    
    # Save inline math blocks ($...$)
    inline_math_blocks = []
    def save_inline_math(match):
        inline_math_blocks.append(match.group(1))
        return f"INLINEMATH{len(inline_math_blocks)-1}PLACEHOLDER"
    
    # Replace LaTeX blocks with placeholders
    content_with_placeholders = re.sub(r'\$\$(.*?)\$\$', save_display_math, markdown_content, flags=re.DOTALL)
    content_with_placeholders = re.sub(r'\$([^\$]+?)\$', save_inline_math, content_with_placeholders)
    
    # Initialize markdown converter with extensions
    md = markdown.Markdown(extensions=['extra'])
    
    # Convert markdown to HTML
    html_content = md.convert(content_with_placeholders)
    
    # Restore LaTeX blocks with proper HTML escaping
    for i, math in enumerate(display_math_blocks):
        # Ensure special characters in LaTeX are properly handled
        placeholder = f"DISPLAYMATH{i}PLACEHOLDER"
        # Use HTML comments to protect LaTeX content
        replacement = f"$$\n{math}\n$$"
        html_content = html_content.replace(placeholder, replacement)
    
    for i, math in enumerate(inline_math_blocks):
        placeholder = f"INLINEMATH{i}PLACEHOLDER"
        replacement = f"${math}$"
        html_content = html_content.replace(placeholder, replacement)
    
    return html_content

def generate_content_html(md_path):
    """Generate just the HTML content from markdown file for insertion in content div."""
    # Parse the markdown file
    front_matter, markdown_content = parse_markdown(md_path)
    
    # Get title from front matter or use filename
    title = front_matter.get('title', Path(md_path).stem)
    
    # Remove duplicate title from markdown content if it exists
    # Check if the markdown content starts with a heading that matches the title
    title_pattern = re.compile(r'^#\s*(.*?)\s*$', re.MULTILINE)
    first_heading_match = title_pattern.search(markdown_content)
    
    if first_heading_match and first_heading_match.group(1).strip() == title.strip():
        # Remove the first heading if it matches the title
        markdown_content = title_pattern.sub('', markdown_content, count=1).strip()
    
    # Convert markdown to HTML
    html_content = convert_markdown_to_html(markdown_content)
    
    return html_content

def main(md_path, out_path):
    """Main function to generate HTML content from markdown and save to output file."""
    # Generate HTML content from markdown
    html_content = generate_content_html(md_path)
    
    # Write the output file
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated HTML content from {md_path}: {out_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python generate_post.py <markdown.md> <output.html>")
        sys.exit(1)
    
    md_path = sys.argv[1]
    out_path = sys.argv[2]
    
    # If the markdown file is not in the current directory but just a filename,
    # check if it exists in the posts directory
    if not os.path.exists(md_path) and not os.path.dirname(md_path):
        posts_path = os.path.join("posts", md_path)
        if os.path.exists(posts_path):
            md_path = posts_path
    
    main(md_path, out_path)