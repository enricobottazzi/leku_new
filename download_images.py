import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def download_and_update_images(directory):
    if not os.path.exists("assets"):
        os.makedirs("assets")

    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')

            for img in soup.find_all('img'):
                src = img.get('src')
                if src and 'hackmd.io' in src:
                    try:
                        response = requests.get(src)
                        response.raise_for_status()  # Raise an exception for bad status codes
                        
                        # Get the image name from the URL
                        parsed_url = urlparse(src)
                        image_name = os.path.basename(parsed_url.path)
                        
                        # Save the image to the assets folder
                        image_path = os.path.join("assets", image_name)
                        with open(image_path, 'wb') as f:
                            f.write(response.content)
                        
                        # Update the src attribute to the local path
                        img['src'] = f"../assets/{image_name}"
                        print(f"Downloaded {src} to {image_path}")

                    except requests.exceptions.RequestException as e:
                        print(f"Error downloading {src}: {e}")

            # Write the modified HTML back to the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))

if __name__ == "__main__":
    download_and_update_images("posts")
