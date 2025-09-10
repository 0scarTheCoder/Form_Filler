#!/usr/bin/env python3
"""
Simple Job Application Form Filler Demo
Works with basic Python libraries to demonstrate the concept
"""

import sys
import os
import json
import time
from pathlib import Path

# Add user site-packages to path
user_site = '/Users/oscar/Library/Python/3.10/lib/python/site-packages'
if user_site not in sys.path and os.path.exists(user_site):
    sys.path.insert(0, user_site)

def load_personal_data():
    """Load personal data from config file"""
    config_path = Path('config/personal_data.json')
    if not config_path.exists():
        print("❌ Personal data file not found. Please run setup first.")
        return None
    
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"❌ Error loading personal data: {e}")
        return None

def setup_personal_data():
    """Interactive setup of personal data"""
    print("Setting up your personal information...")
    
    # Create basic config structure
    config = {
        "personal_info": {
            "first_name": input("First Name: "),
            "last_name": input("Last Name: "),
            "email": input("Email: "),
            "phone": input("Phone: "),
            "address": {
                "street": input("Street Address: "),
                "city": input("City: "),
                "state": input("State/Province: "),
                "zip_code": input("ZIP/Postal Code: "),
                "country": input("Country: ")
            }
        },
        "education": {
            "university": input("University: "),
            "degree": input("Degree: "),
            "graduation_year": input("Graduation Year: ")
        },
        "files": {
            "resume_path": input("Resume file path (or press Enter to skip): ") or None
        }
    }
    
    # Save config
    os.makedirs('config', exist_ok=True)
    with open('config/personal_data.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Personal data saved!")
    return config

def fill_web_form_demo(url):
    """Demo web form filling with Selenium"""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        print(f"🌐 Opening {url}")
        
        # Load personal data
        data = load_personal_data()
        if not data:
            return False
        
        # Setup Chrome driver
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        try:
            # Navigate to the form
            driver.get(url)
            time.sleep(3)
            
            print("🔍 Looking for form fields...")
            
            # Common form field selectors and their data mappings
            field_mappings = {
                # First name fields
                ('input[name*="first"]', 'input[id*="first"]', 'input[placeholder*="first" i]'): 
                    data['personal_info']['first_name'],
                
                # Last name fields
                ('input[name*="last"]', 'input[id*="last"]', 'input[placeholder*="last" i]'): 
                    data['personal_info']['last_name'],
                
                # Email fields
                ('input[type="email"]', 'input[name*="email"]', 'input[id*="email"]'): 
                    data['personal_info']['email'],
                
                # Phone fields
                ('input[type="tel"]', 'input[name*="phone"]', 'input[id*="phone"]'): 
                    data['personal_info']['phone'],
                
                # Address fields
                ('input[name*="address"]', 'input[id*="address"]', 'textarea[name*="address"]'): 
                    f"{data['personal_info']['address']['street']}, {data['personal_info']['address']['city']}",
                
                # City fields
                ('input[name*="city"]', 'input[id*="city"]'): 
                    data['personal_info']['address']['city'],
                
                # University fields
                ('input[name*="school"]', 'input[name*="university"]', 'input[name*="college"]'): 
                    data['education']['university'],
            }
            
            filled_count = 0
            
            # Try to fill each field type
            for selectors, value in field_mappings.items():
                if not value:
                    continue
                    
                field_found = False
                for selector in selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            element = elements[0]  # Use first match
                            if element.is_displayed() and element.is_enabled():
                                # Scroll to element
                                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                time.sleep(0.5)
                                
                                # Clear and fill
                                element.clear()
                                element.send_keys(str(value))
                                
                                print(f"✅ Filled field: {selector} = {value}")
                                filled_count += 1
                                field_found = True
                                break
                    except Exception as e:
                        continue
                
                if field_found:
                    time.sleep(0.5)  # Small delay between fields
            
            print(f"\n📊 Filled {filled_count} fields")
            
            # Show confirmation
            print("\n" + "="*50)
            print("FORM PREVIEW")
            print("="*50)
            print("The form has been filled with your information.")
            print("Please review the page before submitting.")
            print("The browser will stay open so you can review and submit manually.")
            print("="*50)
            
            input("Press Enter to close the browser...")
            
            return filled_count > 0
            
        finally:
            driver.quit()
            
    except ImportError:
        print("❌ Selenium not installed. Run: pip install selenium webdriver-manager")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🤖 Job Application Form Filler - Simple Demo")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--setup':
            setup_personal_data()
        elif sys.argv[1] == '--url' and len(sys.argv) > 2:
            fill_web_form_demo(sys.argv[2])
        else:
            print("Usage:")
            print("  python simple_demo.py --setup")
            print("  python simple_demo.py --url 'https://example.com/careers'")
    else:
        # Interactive mode
        print("1. Setup personal data")
        print("2. Fill a job application form")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            setup_personal_data()
        elif choice == '2':
            # Check if data exists
            if not load_personal_data():
                print("Please setup your personal data first (option 1)")
                return
            
            url = input("Enter job application URL: ").strip()
            if url:
                fill_web_form_demo(url)
        elif choice == '3':
            print("Goodbye! 👋")
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()