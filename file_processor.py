import os
import magic
from pathlib import Path
from playwright.sync_api import sync_playwright

class FileProcessor:
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        
    def detect_file_type(self, file_path: str) -> str:
        """Detect if file is HTML or image."""
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        return file_type
        
    def convert_html_to_image(self, html_path: str, output_format: str = 'png') -> str:
        """Convert HTML file to image using Playwright."""
        # Get absolute paths
        abs_html_path = os.path.abspath(html_path)
        output_filename = f"{Path(html_path).stem}_converted.{output_format}"
        output_path = os.path.abspath(os.path.join(self.upload_folder, output_filename))
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            # Use file:/// protocol with absolute path
            page.goto(f'file:///{abs_html_path.replace("\\", "/")}')
            # Set viewport size to capture full content
            page.set_viewport_size({"width": 1280, "height": 720})
            page.screenshot(path=output_path, full_page=True)
            browser.close()
        
        return output_path
    
    def process_file(self, file_path: str) -> str:
        """Process file and return path to image."""
        file_type = self.detect_file_type(file_path)
        
        if file_type.startswith('text/html'):
            return self.convert_html_to_image(file_path)
        elif file_type.startswith('image/'):
            return file_path
        else:
            raise ValueError(f"Unsupported file type: {file_type}")