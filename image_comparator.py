import cv2
import pytesseract
from difflib import SequenceMatcher
from PIL import Image
import numpy as np
from io import BytesIO
from playwright.sync_api import sync_playwright
import os

class ImageComparator:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

    def compare_images(self, image1_path, image2_path):
        img1 = cv2.imread(image1_path)
        img2 = cv2.imread(image2_path)

        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        text_data1 = pytesseract.image_to_data(gray1, output_type=pytesseract.Output.DICT)
        text_data2 = pytesseract.image_to_data(gray2, output_type=pytesseract.Output.DICT)

        words1 = text_data1['text']
        words2 = text_data2['text']

        matcher = SequenceMatcher(None, words1, words2)
        differences = matcher.get_opcodes()

        outlined_img = img1.copy()
        for tag, i1, i2, j1, j2 in differences:
            if tag != 'equal':
                for idx in range(i1, i2):
                    if idx < len(text_data1['text']) and text_data1['conf'][idx] > 0:
                        x = text_data1['left'][idx]
                        y = text_data1['top'][idx]
                        w = text_data1['width'][idx]
                        h = text_data1['height'][idx]
                        cv2.rectangle(outlined_img, (x-2, y-2), (x + w+2, y + h+2), (0, 255, 255), 3)
                        cv2.rectangle(outlined_img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        output_filename = 'output.png'
        output_path = os.path.join(self.upload_folder, output_filename)
        cv2.imwrite(output_path, outlined_img)

        return output_filename

    def compare_images_in_memory(self, img1_np, img2_np):
        """Compare two images using numpy arrays directly."""
        try:
            # Make copies to avoid modifying originals
            img1_working = img1_np.copy()
            img2_working = img2_np.copy()
            
            # Convert to BGR for OpenCV if in RGB
            if len(img1_working.shape) == 3:
                img1_working = cv2.cvtColor(img1_working, cv2.COLOR_RGB2BGR)
                img2_working = cv2.cvtColor(img2_working, cv2.COLOR_RGB2BGR)
                
            # Convert to grayscale for text detection
            gray1 = cv2.cvtColor(img1_working, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2_working, cv2.COLOR_BGR2GRAY)

            # Extract text data
            text_data1 = pytesseract.image_to_data(gray1, output_type=pytesseract.Output.DICT)
            text_data2 = pytesseract.image_to_data(gray2, output_type=pytesseract.Output.DICT)

            words1 = text_data1['text']
            words2 = text_data2['text']

            # Find differences
            matcher = SequenceMatcher(None, words1, words2)
            differences = matcher.get_opcodes()

            # Create output image with highlighted differences
            outlined_img = img1_np.copy()  # Use original image for output
            diff_areas = []

            for tag, i1, i2, j1, j2 in differences:
                if tag != 'equal':
                    for idx in range(i1, i2):
                        if idx < len(text_data1['text']) and text_data1['conf'][idx] > 0:
                            x = text_data1['left'][idx]
                            y = text_data1['top'][idx]
                            w = text_data1['width'][idx]
                            h = text_data1['height'][idx]
                            
                            # Draw rectangles using RGB colors
                            cv2.rectangle(outlined_img, (x-2, y-2), (x + w+2, y + h+2), (255, 255, 0), 3)  # Yellow
                            cv2.rectangle(outlined_img, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Red

            return outlined_img

        except Exception as e:
            print(f"Debug - img1_np shape: {img1_np.shape if img1_np is not None else 'None'}")
            print(f"Debug - img2_np shape: {img2_np.shape if img2_np is not None else 'None'}")
            raise Exception(f"Error comparing images in memory: {str(e)}")

    def compare_with_multiple(self, master_image_path, child_image_paths):
        results = {}
        for child_image_path in child_image_paths:
            result = self.compare_images(master_image_path, child_image_path)
            results[child_image_path] = result
        return results

    def html_to_image(self, html_path, output_image_path):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f'file://{html_path}')
            page.screenshot(path=output_image_path)
            browser.close()