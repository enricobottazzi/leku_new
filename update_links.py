import os
from bs4 import BeautifulSoup

def is_external_link(link):
    """
    Checks if a link is external (starts with http:// or https://).
    """
    href = link.get('href', '')
    return href.startswith('http://') or href.startswith('https://')

def update_links_in_file(filepath):
    """
    Opens an HTML file, finds all external links, and adds target="_blank" to them.
    Internal links are reverted to open in the same tab if they were modified.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')
        links = soup.find_all('a', href=True)

        if not links:
            return

        modified = False
        for link in links:
            if is_external_link(link):
                if not link.has_attr('target') or link.get('target') != '_blank':
                    link['target'] = '_blank'
                    link['rel'] = 'noopener noreferrer'
                    modified = True
            else:
                # This is an internal link, so we make sure it doesn't open in a new tab
                if link.has_attr('target'):
                    del link['target']
                    del link['rel']
                    modified = True

        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(f"Updated links in: {filepath}")

    except Exception as e:
        print(f"Error processing file {filepath}: {e}")

def find_and_update_html_files(root_dir):
    """
    Recursively finds all HTML files in a directory and updates the links.
    """
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                update_links_in_file(filepath)

if __name__ == "__main__":
    current_directory = os.getcwd()
    find_and_update_html_files(current_directory)
    print("\nLink update process complete.")