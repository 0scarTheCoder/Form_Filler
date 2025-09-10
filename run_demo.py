#!/usr/bin/env python3
"""
Demo script for Job Application Form Filler (Web Mode Only)
"""

import sys
import os

# Add user site-packages to path
user_site = '/Users/oscar/Library/Python/3.10/lib/python/site-packages'
if user_site not in sys.path and os.path.exists(user_site):
    sys.path.insert(0, user_site)

# Add src to path
sys.path.append('src')

def test_web_automation():
    """Test web automation functionality"""
    print("Testing web automation components...")
    
    try:
        # Test selenium
        from selenium import webdriver
        print("✓ Selenium imported successfully")
        
        # Test data manager
        from data_manager import DataManager
        dm = DataManager()
        print("✓ Data manager loaded")
        
        # Check if personal data is configured
        try:
            data = dm.load_data()
            if data.personal_info.first_name == "YOUR_FIRST_NAME":
                print("⚠ Personal data needs configuration")
                return False
            else:
                print("✓ Personal data configured")
        except Exception as e:
            print(f"❌ Personal data error: {e}")
            return False
        
        print("\n✅ Web automation is ready!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def quick_setup():
    """Quick setup guide"""
    print("\n" + "="*50)
    print("JOB APPLICATION FORM FILLER - QUICK SETUP")
    print("="*50)
    
    print("\n1. First, configure your personal data:")
    print("   Edit: config/personal_data.json")
    print("   Replace all YOUR_* placeholders with your actual information")
    
    print("\n2. Test with a job application:")
    print("   python run_demo.py --url 'https://company.com/careers/apply'")
    
    print("\n3. For AI-powered field matching (optional):")
    print("   - Get an Anthropic API key from https://console.anthropic.com")
    print("   - Copy .env.example to .env")
    print("   - Add your API key to the .env file")
    
    print("\nThis version focuses on web form automation (most reliable).")
    print("Screen automation can be added later with additional setup.")

def fill_form(url):
    """Fill a web form"""
    try:
        # Import form filler without screen components
        from form_filler import FormFiller
        
        # Create filler with web-only mode
        filler = FormFiller()
        print(f"\nFilling form at: {url}")
        
        success = filler.fill_web_form(url)
        
        if success:
            print("✅ Form filled successfully!")
        else:
            print("❌ Failed to fill form")
            
    except Exception as e:
        print(f"❌ Error filling form: {e}")
    finally:
        try:
            filler.close_driver()
        except:
            pass

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            test_web_automation()
        elif sys.argv[1] == '--url' and len(sys.argv) > 2:
            fill_form(sys.argv[2])
        else:
            print("Usage:")
            print("  python run_demo.py --test")
            print("  python run_demo.py --url 'https://example.com/apply'")
    else:
        if test_web_automation():
            quick_setup()
        else:
            print("\n❌ Setup incomplete. Please configure your personal data first.")

if __name__ == "__main__":
    main()