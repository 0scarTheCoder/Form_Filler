import cv2
import numpy as np
import pyautogui
import pytesseract
from PIL import Image, ImageDraw
from typing import List, Dict, Tuple, Optional
import base64
from dataclasses import dataclass
import re

@dataclass
class FormField:
    x: int
    y: int
    width: int
    height: int
    field_type: str  # 'input', 'textarea', 'select', 'file'
    label: Optional[str] = None
    placeholder: Optional[str] = None
    confidence: float = 0.0

class ScreenAnalyzer:
    def __init__(self):
        self.screenshot = None
        self.form_fields = []
        
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Capture screenshot of screen or specified region"""
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
        
        self.screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return self.screenshot
    
    def detect_form_fields(self, screenshot: Optional[np.ndarray] = None) -> List[FormField]:
        """Detect form fields using computer vision"""
        if screenshot is None:
            screenshot = self.screenshot
        
        if screenshot is None:
            raise ValueError("No screenshot available. Call capture_screen() first.")
        
        # Convert to grayscale
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Detect rectangular regions (potential form fields)
        form_fields = []
        
        # Method 1: Edge detection for input fields
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter potential input fields by size and aspect ratio
            if (20 < w < 800 and 15 < h < 100 and 
                cv2.contourArea(contour) > 300):
                
                aspect_ratio = w / h
                if 1.5 < aspect_ratio < 20:  # Typical input field ratios
                    field_type = self._classify_field_type(x, y, w, h, gray)
                    label = self._extract_nearby_text(x, y, w, h, gray)
                    
                    form_fields.append(FormField(
                        x=x, y=y, width=w, height=h,
                        field_type=field_type, label=label,
                        confidence=0.7
                    ))
        
        # Method 2: Template matching for common UI elements
        form_fields.extend(self._detect_buttons_and_uploads(gray))
        
        # Remove duplicates and overlapping fields
        form_fields = self._remove_duplicates(form_fields)
        
        self.form_fields = form_fields
        return form_fields
    
    def _classify_field_type(self, x: int, y: int, w: int, h: int, gray: np.ndarray) -> str:
        """Classify the type of form field based on visual characteristics"""
        # Extract the field region
        field_region = gray[y:y+h, x:x+w]
        
        # Analyze characteristics
        if h > 80:
            return 'textarea'
        elif w > 400 and h < 50:
            return 'input'
        elif 100 < w < 200 and 20 < h < 40:
            return 'select'
        else:
            return 'input'
    
    def _extract_nearby_text(self, x: int, y: int, w: int, h: int, gray: np.ndarray) -> Optional[str]:
        """Extract text labels near form fields using OCR"""
        # Define search regions around the field
        margin = 20
        height_expansion = 40
        
        # Search to the left and above
        search_regions = [
            # Left side
            gray[max(0, y-margin):y+h+margin, max(0, x-200):x],
            # Above
            gray[max(0, y-height_expansion):y, x:x+w],
            # Right side (for checkbox-like fields)
            gray[max(0, y-margin):y+h+margin, x+w:min(gray.shape[1], x+w+200)]
        ]
        
        for region in search_regions:
            if region.size == 0:
                continue
                
            try:
                text = pytesseract.image_to_string(region, config='--psm 8').strip()
                # Clean and validate the extracted text
                text = re.sub(r'[^\w\s]', '', text).strip()
                if len(text) > 2 and len(text) < 50:
                    return text
            except:
                continue
        
        return None
    
    def _detect_buttons_and_uploads(self, gray: np.ndarray) -> List[FormField]:
        """Detect buttons and file upload fields using template matching"""
        fields = []
        
        # Look for file upload patterns using text detection
        try:
            # Use OCR to find file upload related text
            text_data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            upload_keywords = ['upload', 'choose file', 'browse', 'attach', 'select file', 'resume', 'cv']
            
            for i in range(len(text_data['text'])):
                text = text_data['text'][i].lower()
                confidence = int(text_data['conf'][i])
                
                if confidence > 30 and any(keyword in text for keyword in upload_keywords):
                    x = text_data['left'][i]
                    y = text_data['top'][i]
                    w = text_data['width'][i]
                    h = text_data['height'][i]
                    
                    # Expand the region to include the actual clickable area
                    fields.append(FormField(
                        x=max(0, x-20), y=max(0, y-10),
                        width=w+40, height=h+20,
                        field_type='file',
                        label=text_data['text'][i],
                        confidence=confidence/100.0
                    ))
        except Exception as e:
            print(f"OCR error in button detection: {e}")
        
        return fields
    
    def _remove_duplicates(self, fields: List[FormField]) -> List[FormField]:
        """Remove duplicate and overlapping form fields"""
        if not fields:
            return fields
        
        # Sort by confidence (highest first)
        fields.sort(key=lambda f: f.confidence, reverse=True)
        
        filtered_fields = []
        for field in fields:
            is_duplicate = False
            for existing in filtered_fields:
                # Check for significant overlap
                overlap_x = max(0, min(field.x + field.width, existing.x + existing.width) - 
                              max(field.x, existing.x))
                overlap_y = max(0, min(field.y + field.height, existing.y + existing.height) - 
                              max(field.y, existing.y))
                overlap_area = overlap_x * overlap_y
                
                field_area = field.width * field.height
                existing_area = existing.width * existing.height
                
                overlap_ratio = overlap_area / min(field_area, existing_area)
                
                if overlap_ratio > 0.5:  # 50% overlap threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered_fields.append(field)
        
        return filtered_fields
    
    def visualize_detected_fields(self) -> Image.Image:
        """Create a visual representation of detected form fields"""
        if self.screenshot is None:
            raise ValueError("No screenshot available")
        
        # Convert OpenCV image to PIL
        pil_image = Image.fromarray(cv2.cvtColor(self.screenshot, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)
        
        colors = {
            'input': 'red',
            'textarea': 'blue',
            'select': 'green',
            'file': 'orange'
        }
        
        for field in self.form_fields:
            color = colors.get(field.field_type, 'purple')
            
            # Draw rectangle around field
            draw.rectangle(
                [field.x, field.y, field.x + field.width, field.y + field.height],
                outline=color, width=2
            )
            
            # Add label if available
            if field.label:
                draw.text((field.x, field.y - 20), 
                         f"{field.field_type}: {field.label}", 
                         fill=color)
        
        return pil_image
    
    def get_field_at_coordinates(self, x: int, y: int) -> Optional[FormField]:
        """Get form field at specific coordinates"""
        for field in self.form_fields:
            if (field.x <= x <= field.x + field.width and 
                field.y <= y <= field.y + field.height):
                return field
        return None