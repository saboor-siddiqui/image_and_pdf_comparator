from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, NamedTuple
import cv2
import numpy as np
import os
from pathlib import Path
from typing import List, Dict, Union
from file_processor import FileProcessor

class ImageDifference(NamedTuple):
    area: Tuple[int, int, int, int]  # x, y, width, height
    difference_percentage: float

@dataclass
class ComparisonResult:
    child_image_name: str
    difference_score: float
    difference_areas: List[ImageDifference]
    output_filename: str
    comparison_status: str
    similarity_percentage: float

class MultipleImageComparator:
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        self.file_processor = FileProcessor(upload_folder)
        self.similarity_threshold = 0.95  # 95% similarity threshold
        
    def validate_inputs(self, parent_path: str, child_paths: List[str]) -> None:
        """Validate input parameters."""
        if not os.path.exists(parent_path):
            raise ValueError("Parent image not found")
            
        if len(child_paths) < self.min_images:
            raise ValueError(f"At least {self.min_images} comparison images required")
            
        for path in child_paths:
            if not os.path.exists(path):
                raise ValueError(f"Child image not found: {path}")

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for comparison."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Normalize
        normalized = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(normalized, (5, 5), 0)
        return blurred

    def calculate_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate similarity score between two images."""
        # Using Structural Similarity Index (SSIM)
        score = cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)[0][0]
        return float(score)

    def find_differences(self, parent_img: np.ndarray, child_img: np.ndarray) -> List[ImageDifference]:
        """Find and quantify differences between images."""
        # Calculate absolute difference
        diff = cv2.absdiff(parent_img, child_img)
        
        # Threshold the difference image
        thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)[1]
        
        # Find contours of differences
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        differences = []
        total_pixels = parent_img.shape[0] * parent_img.shape[1]
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if area > 100:  # Filter out tiny differences
                diff_percentage = (area / total_pixels) * 100
                differences.append(ImageDifference((x, y, w, h), diff_percentage))
                
        return differences

    def generate_comparison_visualization(self, 
                                       parent_img: np.ndarray,
                                       child_img: np.ndarray, 
                                       differences: List[ImageDifference],
                                       child_name: str) -> str:
        """Generate visual comparison with highlighted differences."""
        # Create side-by-side comparison
        result_img = np.hstack((parent_img, child_img))
        height, width = parent_img.shape[:2]
        
        # Draw differences on both images
        for diff in differences:
            x, y, w, h = diff.area
            # Draw on parent image
            cv2.rectangle(result_img, (x, y), (x + w, y + h), (0, 255, 255), 2)
            # Draw on child image (offset by width)
            cv2.rectangle(result_img, (x + width, y), (x + w + width, y + h), (0, 255, 255), 2)
            
            # Add difference percentage
            cv2.putText(result_img, f"{diff.difference_percentage:.1f}%", 
                       (x + width, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (0, 255, 255), 1)

        # Generate unique output filename
        output_filename = f"comparison_{Path(child_name).stem}.png"
        output_path = os.path.join(self.upload_folder, output_filename)
        cv2.imwrite(output_path, result_img)
        
        return output_filename

    def compare_multiple(self, parent_path: str, child_paths: List[str]) -> Dict[str, ComparisonResult]:
        """Compare parent file with multiple child files."""
        self.validate_inputs(parent_path, child_paths)
        
        # Process parent file
        parent_img_path = self.file_processor.process_file(parent_path)
        parent_img = self.validate_image(parent_img_path)
        parent_preprocessed = self.preprocess_image(parent_img)
        
        results = {}
        for child_path in child_paths:
            try:
                # Process child file
                child_img_path = self.file_processor.process_file(child_path)
                child_img = self.validate_image(child_img_path)
                child_preprocessed = self.preprocess_image(child_img)
                
                # Rest of the comparison logic remains same
                diff_score, highlighted_areas = self.compare_single_pair(
                    parent_preprocessed, child_preprocessed
                )
                
                output_filename = self.generate_comparison_visualization(
                    parent_img, child_img, highlighted_areas, 
                    os.path.basename(child_path)
                )
                
                status = "Similar" if diff_score < 50 else "Different"
                
                results[child_path] = ComparisonResult(
                    child_image_name=os.path.basename(child_path),
                    difference_score=diff_score,
                    difference_areas=highlighted_areas,
                    output_filename=output_filename,
                    comparison_status=status,
                    similarity_percentage=(1 - diff_score/100) * 100
                )
                
            except Exception as e:
                print(f"Error comparing {child_path}: {str(e)}")
                continue
                
        return results