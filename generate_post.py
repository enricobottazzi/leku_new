#!/usr/bin/env python3
"""
generate_post.py

Automates adding a new blog post from a markdown file.

Usage:
    python generate_post.py md/cryptography_cheatsheet.md --date 2026-02-10
    python generate_post.py md/cryptography_cheatsheet.md              # uses today's date

What it does:
  1. Parses the markdown file to extract the title (first # heading) and body.
  2. Converts markdown to HTML, preserving LaTeX math and code blocks.
  3. Wraps the content in the full post HTML template (sidebar, MathJax, theme sync, etc.).
  4. Writes the result to posts/<slug>.html
  5. Inserts a new entry into index.html in chronological order (newest first).
"""

import sys
import re
import argparse
import markdown
from pathlib import Path
from datetime import date


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

def parse_markdown(path: str):
    """Return (title, body_md) from a markdown file.

    The title is taken from the first '# ...' heading.  If the file has YAML
    front-matter (---…---) a 'title' key there takes precedence.
    """
    text = Path(path).read_text(encoding="utf-8")

    # Try YAML front-matter
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, flags=re.S)
    title = None
    body_md = text

    if fm_match:
        import yaml
        fm = yaml.safe_load(fm_match.group(1)) or {}
        title = fm.get("title")
        body_md = fm_match.group(2)

    # Sanitize stray </p> lines that sometimes leak from copy-paste
    body_md = re.sub(r"(?m)^\s*</p>\s*$", "", body_md)

    # Extract title from first # heading if not already found
    if title is None:
        heading_match = re.search(r"^#\s+(.+)$", body_md, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1).strip()
        else:
            title = Path(path).stem.replace("_", " ").replace("-", " ").title()

    # Remove the first heading from the body (it goes into the <h1> tag)
    body_md = re.sub(r"^#\s+.+\n*", "", body_md, count=1).strip()

    return title, body_md


# ---------------------------------------------------------------------------
# Markdown → HTML conversion  (preserves LaTeX)
# ---------------------------------------------------------------------------

def convert_markdown_to_html(markdown_content: str) -> str:
    """Convert markdown to HTML, protecting LaTeX math blocks."""
    content = markdown_content

    # Strip Hugo shortcodes
    content = re.sub(r"\{\{<rawhtml>\}\}", "", content)
    content = re.sub(r"\{\{</rawhtml>\}\}", "", content)

    # Protect display math ($$...$$)
    display_blocks: list[str] = []
    def _save_display(m):
        display_blocks.append(m.group(1))
        return f"DISPLAYMATH{len(display_blocks)-1}PLACEHOLDER"

    # Protect inline math ($...$)
    inline_blocks: list[str] = []
    def _save_inline(m):
        inline_blocks.append(m.group(1))
        return f"INLINEMATH{len(inline_blocks)-1}PLACEHOLDER"

    content = re.sub(r"\$\$(.*?)\$\$", _save_display, content, flags=re.DOTALL)
    content = re.sub(r"\$([^\$]+?)\$", _save_inline, content)

    # Convert with Python-Markdown
    md = markdown.Markdown(extensions=["extra", "fenced_code", "codehilite"])
    html = md.convert(content)

    # Restore math blocks
    for i, math in enumerate(display_blocks):
        html = html.replace(f"DISPLAYMATH{i}PLACEHOLDER", f"$$\n{math}\n$$")
    for i, math in enumerate(inline_blocks):
        html = html.replace(f"INLINEMATH{i}PLACEHOLDER", f"${math}$")

    # Rewrite HackMD image URLs to local assets
    html = re.sub(
        r'src="https://hackmd\.io/_uploads/([^"]+)"',
        r'src="../assets/\1"',
        html,
    )

    return html


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

POST_TEMPLATE = """\
<!DOCTYPE html>

<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Leku - {title}</title>
<link as="font" crossorigin="" href="../JetBrainsMono-2.304/fonts/webfonts/JetBrainsMono-Regular.woff2" rel="preload" type="font/woff2"/>
<link as="font" crossorigin="" href="../JetBrainsMono-2.304/fonts/webfonts/JetBrainsMono-Bold.woff2" rel="preload" type="font/woff2"/>
<script>
    // Apply saved colors before first paint to avoid flash
    (function() {{
      try {{
        var bg = localStorage.getItem('customBgColor');
        var fg = localStorage.getItem('customFontColor');
        var css = '';
        if (bg) css += 'body{{background-color:' + bg + ' !important;}}';
        if (fg) {{
          css += 'body{{color:' + fg + ' !important;}}';
          css += '.sidebar{{border-right-color:' + fg + ' !important;}}';
          css += '.post-date,.sidebar li,.post-link{{color:' + fg + ' !important;}}';
        }}
        if (css) {{
          var s = document.createElement('style');
          s.id = 'early-theme';
          s.textContent = css;
          document.head.appendChild(s);
        }}
      }} catch (_) {{}}
    }})();
  </script>
<link href="../styles.css" rel="stylesheet"/>
<!-- MathJax for LaTeX support -->
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script>
    // Configure MathJax (v3) before loading the script
    window.MathJax = {{
      tex: {{
        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
        processEscapes: true
      }},
      options: {{
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
      }}
    }};
  </script>
<script async="" id="MathJax-script" src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
<div class="wrapper">
<nav class="sidebar">
<ul>
<li><a href="../index.html">index</a></li>
<li><a href="../index.html#about">about</a></li>
</ul>
</nav>
<main class="content">
<article class="post">
<header>
<h1 class="post-title">{title}</h1>
<div class="post-date">{date}</div>
</header>
<section class="post-content">
{content}
</section>
</article>
</main>
</div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# index.html updater
# ---------------------------------------------------------------------------

def update_index(index_path: str, slug: str, title: str, post_date: str):
    """Insert a new post entry into index.html in chronological order (newest first).

    If an entry for the same slug already exists it is replaced.
    """
    html = Path(index_path).read_text(encoding="utf-8")
    href = f"posts/{slug}.html"

    # Remove existing entry for the same slug (if re-generating)
    # Match the full <li class="post-item">…</li> block that contains our href
    existing_pattern = re.compile(
        r'<li class="post-item">\s*\n?\s*<a class="post-link" href="'
        + re.escape(href)
        + r'"[^>]*>.*?</a>\s*\n?\s*<span class="post-date">[^<]*</span>\s*\n?\s*</li>',
        re.DOTALL,
    )
    html = existing_pattern.sub("", html)

    # Build the new entry
    new_entry = (
        f'<li class="post-item">\n'
        f'    <a class="post-link" href="{href}">{title}</a>\n'
        f'    <span class="post-date">{post_date}</span>\n'
        f'</li>'
    )

    # Find all existing post entries and their dates to insert in order
    entry_pattern = re.compile(
        r'(<li class="post-item">.*?<span class="post-date">)(\d{4}-\d{2}-\d{2})(</span>\s*\n?\s*</li>)',
        re.DOTALL,
    )

    entries = list(entry_pattern.finditer(html))

    if not entries:
        # No existing entries — insert right after <ul class="posts" id="posts-list">
        html = html.replace(
            '<ul class="posts" id="posts-list">',
            f'<ul class="posts" id="posts-list">\n{new_entry}',
        )
    else:
        # Find the right position (newest first)
        inserted = False
        for entry_match in entries:
            entry_date = entry_match.group(2)
            if post_date >= entry_date:
                # Insert before this entry
                html = html[:entry_match.start()] + new_entry + "\n" + html[entry_match.start():]
                inserted = True
                break
        if not inserted:
            # This post is the oldest — insert after the last entry
            last = entries[-1]
            insert_pos = last.end()
            html = html[:insert_pos] + "\n" + new_entry + html[insert_pos:]

    # Clean up any double blank lines that may have been introduced
    html = re.sub(r"\n{3,}", "\n\n", html)

    Path(index_path).write_text(html, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a blog post HTML from a markdown file and update index.html."
    )
    parser.add_argument("markdown_file", help="Path to the markdown source (e.g. md/my_post.md)")
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Publication date in YYYY-MM-DD format (default: today)",
    )
    args = parser.parse_args()

    md_path = Path(args.markdown_file)
    if not md_path.exists():
        print(f"Error: {md_path} does not exist.")
        sys.exit(1)

    post_date = args.date
    slug = md_path.stem  # e.g. "cryptography_cheatsheet"

    # Resolve project root (script lives at the repo root)
    project_root = Path(__file__).resolve().parent
    posts_dir = project_root / "posts"
    posts_dir.mkdir(exist_ok=True)
    index_path = project_root / "index.html"

    # 1. Parse markdown
    title, body_md = parse_markdown(str(md_path))
    print(f"Title:  {title}")
    print(f"Date:   {post_date}")
    print(f"Slug:   {slug}")

    # 2. Convert to HTML
    html_content = convert_markdown_to_html(body_md)

    # 3. Render full post page
    full_html = POST_TEMPLATE.format(
        title=title,
        date=post_date,
        content=html_content,
    )

    # 4. Write post file
    out_path = posts_dir / f"{slug}.html"
    out_path.write_text(full_html, encoding="utf-8")
    print(f"Post:   {out_path}")

    # 5. Update index.html
    if index_path.exists():
        update_index(str(index_path), slug, title, post_date)
        print(f"Index:  {index_path} updated")
    else:
        print(f"Warning: {index_path} not found — skipping index update.")

    print("\nDone! You can optionally run `python download_images.py` to download HackMD images.")


if __name__ == "__main__":
    main()
