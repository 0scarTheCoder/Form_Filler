#!/usr/bin/env python3
"""
Environment setup for Form Filler
"""

import sys
import os

# Add user site-packages to path if not already there
user_site = '/Users/oscar/Library/Python/3.10/lib/python/site-packages'
if user_site not in sys.path and os.path.exists(user_site):
    sys.path.insert(0, user_site)

# Test all imports
def test_imports():
    print("Testing imports with adjusted Python path...")
    
    imports_status = []
    
    modules = [
        ('selenium', 'Selenium WebDriver'),
        ('pyautogui', 'PyAutoGUI'),
        ('cv2', 'OpenCV'),
        ('pytesseract', 'Pytesseract'),
        ('PIL', 'Pillow'),
        ('pydantic', 'Pydantic'),
        ('anthropic', 'Anthropic (optional)')
    ]
    
    for module, name in modules:
        try:
            __import__(module)
            print(f"✓ {name}")
            imports_status.append(True)
        except ImportError as e:
            print(f"❌ {name} - {e}")
            imports_status.append(False)
    
    return all(imports_status)

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ All imports successful! Form Filler is ready.")
    else:
        print("\n❌ Some imports failed. Please install missing packages.")
        sys.exit(1)