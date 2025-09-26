import argparse
import os
from typing import List

import cv2
import numpy as np


class CoinDefectDetector:
    def __init__(self, low_threshold: int = 50, high_threshold: int = 150):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
    
    def _load_image(self, image_path: str) -> np.ndarray:
        image = cv2.imread(filename=image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        return image
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Convert to grayscale, apply otsu thresholding and clean the image."""
        diff_gray = cv2.cvtColor(src=image, code=cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(src=diff_gray, thresh=0, maxval=255, type=(cv2.THRESH_BINARY + cv2.THRESH_OTSU))
        
        # Clean up the mask with morphological operations
        kernel = np.ones(shape=(5, 5), dtype=np.uint8)
        thresh = cv2.morphologyEx(src=thresh, op=cv2.MORPH_CLOSE, kernel=kernel)
        thresh = cv2.morphologyEx(src=thresh, op=cv2.MORPH_OPEN, kernel=kernel)
        return thresh
    
    def _find_contours(self, image: np.ndarray) -> List[np.ndarray]:
        """Find contours in binary image."""
        edges = cv2.Canny(image=image, threshold1=self.low_threshold, threshold2=self.high_threshold) 
        contours, _ = cv2.findContours(image=edges, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
        return contours
    
    def detect_defects(self, image_paths: List[str], reference_index: int = 0) -> dict:
        """
        Detect defects in coin images.
        
        Args:
            image_paths (List[str]): List of paths to coin images
            reference_index (int): Index of reference image without defects
            
        Returns:
            Dictionary with results
        """
        if len(image_paths) < 2:
            raise ValueError("Need at least 2 images for comparison")
        
        if reference_index >= len(image_paths):
            raise ValueError("Reference index out of range")
        
        # Load all images
        images = []
        for path in image_paths:
            image = self._load_image(image_path=path)
            images.append(image)
            
        # Find anomaly by maximum difference from reference
        reference = images[reference_index]
        max_diff = 0
        anomaly_index = reference_index
        
        for i, image in enumerate(images):
            if i == reference_index:
                continue
            diff = cv2.absdiff(src1=reference, src2=image)
            total_diff = np.sum(a=diff)
            
            if total_diff > max_diff:
                max_diff = total_diff
                anomaly_index = i

        if max_diff <= self.low_threshold:
            return {
                'success': False
            }
            
        # Get binary mask of differences
        thresh = self._preprocess_image(image=diff)

        # Find contours of differences
        contours = self._find_contours(image=thresh)
        
        # Create result image
        result = images[anomaly_index].copy()
        
        # Highlight differences
        cv2.drawContours(image=result, contours=contours, contourIdx=-1, color=(0, 0, 255), thickness=5)
        
        return {
            'anomaly_index': anomaly_index,
            'defect_contours': contours,
            'highlighted_image': result,
            'difference_score': max_diff,
            'success': True
        }
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect defects in coin images")
    parser.add_argument('-d', '--dir', type=str, default='coins', help='Directory containing the coin images')
    parser.add_argument('-s', '--standart', type=str, default='coin1.png', help='Filename of the standard coin')
    parser.add_argument('-o', '--out', type=str, default='result', help='Output directory')
    args = parser.parse_args()
    
    if not os.path.isdir(args.dir):
        raise ValueError(f"Directory {args.dir} does not exist")
    
    image_files = [f for f in os.listdir(args.dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_paths = [os.path.join(args.dir, f) for f in image_files]
    
    if args.standart not in image_files:
        raise ValueError(f"Standard coin file {args.standart} not found in directory {args.dir}")
    
    reference_index = image_files.index(args.standart)

    detector = CoinDefectDetector()
    results = detector.detect_defects(image_paths=image_paths, reference_index=reference_index)
    
    if results['success']:
        print(f"Defect found in image {image_paths[ results['anomaly_index'] ]}")
        os.makedirs(args.out, exist_ok=True)
        cv2.imwrite(f'{args.out}/defect.jpg', results['highlighted_image'])
    else:
        print("Defect not found")