import os
import mimetypes
from pathlib import Path
from weasyprint import HTML
import magic

class FileProcessor:
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        
    def detect_file_type(self, file_path: str) -> str:
        """Detect if file is HTML or image."""
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        return file_type
        
    def convert_html_to_image(self, html_path: str, output_format: str = 'png') -> str:
        """Convert HTML file to image using WeasyPrint."""
        output_filename = f"{Path(html_path).stem}_converted.{output_format}"
        output_path = os.path.join(self.upload_folder, output_filename)
        
        HTML(html_path).write_png(output_path) if output_format == 'png' else HTML(html_path).write_jpeg(output_path)
        
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