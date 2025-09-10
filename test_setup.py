#!/usr/bin/env python3
"""
Test script to verify the form filler setup
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import selenium
        print("✓ Selenium")
    except ImportError:
        print("❌ Selenium - run 'pip install selenium'")
        return False
    
    try:
        import pyautogui
        print("✓ PyAutoGUI")
    except ImportError:
        print("❌ PyAutoGUI - run 'pip install pyautogui'")
        return False
    
    try:
        import cv2
        print("✓ OpenCV")
    except ImportError:
        print("❌ OpenCV - run 'pip install opencv-python'")
        return False
    
    try:
        import pytesseract
        print("✓ Pytesseract")
    except ImportError:
        print("❌ Pytesseract - run 'pip install pytesseract'")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow")
    except ImportError:
        print("❌ Pillow - run 'pip install pillow'")
        return False
    
    try:
        import pydantic
        print("✓ Pydantic")
    except ImportError:
        print("❌ Pydantic - run 'pip install pydantic'")
        return False
    
    return True

def test_structure():
    """Test if project structure is correct"""
    print("\nTesting project structure...")
    
    required_dirs = ['src', 'config', 'data']
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✓ {dir_name}/ directory")
        else:
            print(f"❌ {dir_name}/ directory missing")
            return False
    
    required_files = [
        'src/main.py',
        'src/form_filler.py',
        'src/data_manager.py',
        'src/screen_analyzer.py',
        'src/field_matcher.py',
        'config/personal_data.json'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True

def test_config():
    """Test configuration file"""
    print("\nTesting configuration...")
    
    sys.path.append('src')
    
    try:
        from data_manager import DataManager
        dm = DataManager()
        data = dm.load_data()
        
        # Check if placeholder values are still present
        if data.personal_info.first_name == "YOUR_FIRST_NAME":
            print("⚠ Personal data still contains placeholder values")
            print("  Run 'python src/main.py --setup' to configure")
        else:
            print("✓ Personal data configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    print("Form Filler Setup Test")
    print("=" * 30)
    
    success = True
    
    success &= test_imports()
    success &= test_structure()
    success &= test_config()
    
    print("\n" + "=" * 30)
    if success:
        print("✅ All tests passed! Form Filler is ready to use.")
        print("\nNext steps:")
        print("1. Configure your personal data: python src/main.py --setup")
        print("2. Try filling a form: python src/main.py --url 'https://example.com'")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()