#!/usr/bin/env python3
"""
Job Application Form Filler
Automates filling of job application forms with personal data
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

# Add the src directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from form_filler import FormFiller
from data_manager import DataManager

def setup_personal_data():
    """Interactive setup of personal data"""
    print("Welcome to Job Application Form Filler!")
    print("Let's set up your personal information first.\n")
    
    data_manager = DataManager()
    
    # Check if config already exists
    try:
        existing_data = data_manager.load_data()
        print("Found existing personal data configuration.")
        print("Would you like to update it? (y/n): ", end="")
        if not input().lower().startswith('y'):
            return
    except FileNotFoundError:
        print("No existing configuration found. Let's create one.")
    
    print("\nPlease update your personal information in:")
    print(f"  {os.path.abspath('config/personal_data.json')}")
    print("\nMake sure to:")
    print("1. Replace all placeholder values with your actual information")
    print("2. Update file paths to point to your actual resume, cover letter, etc.")
    print("3. Set your preferences for salary, start date, etc.")
    print("\nPress Enter when done...")
    input()
    
    # Validate the configuration
    try:
        data = data_manager.load_data()
        print("✓ Configuration loaded successfully!")
        
        # Check file paths
        if data.files.resume_path and not Path(data.files.resume_path).exists():
            print(f"⚠ Warning: Resume file not found at {data.files.resume_path}")
        if data.files.cover_letter_path and not Path(data.files.cover_letter_path).exists():
            print(f"⚠ Warning: Cover letter file not found at {data.files.cover_letter_path}")
        if data.files.transcript_path and not Path(data.files.transcript_path).exists():
            print(f"⚠ Warning: Transcript file not found at {data.files.transcript_path}")
            
    except Exception as e:
        print(f"❌ Error in configuration: {e}")
        sys.exit(1)

def fill_web_form(url: str, anthropic_key: Optional[str] = None):
    """Fill a web form at the given URL"""
    filler = FormFiller(anthropic_api_key=anthropic_key)
    
    try:
        print(f"Filling form at: {url}")
        success = filler.fill_web_form(url)
        
        if success:
            print("✓ Form filled successfully!")
        else:
            print("❌ Failed to fill form")
            
    except KeyboardInterrupt:
        print("\n⚠ Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        filler.close_driver()

def fill_screen_form(anthropic_key: Optional[str] = None):
    """Fill form fields detected on screen"""
    filler = FormFiller(anthropic_api_key=anthropic_key)
    
    try:
        print("Screen form filling mode")
        print("Position your cursor over the form you want to fill")
        print("Press Enter when ready...")
        input()
        
        print("Analyzing screen in 3 seconds...")
        import time
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        success = filler.fill_screen_form()
        
        if success:
            print("✓ Screen form filled successfully!")
        else:
            print("❌ Failed to fill screen form")
            
    except KeyboardInterrupt:
        print("\n⚠ Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def create_site_mapping(url: str, anthropic_key: Optional[str] = None):
    """Create custom field mapping for a specific site"""
    filler = FormFiller(anthropic_api_key=anthropic_key)
    
    try:
        print(f"Creating field mapping for: {url}")
        mappings = filler.create_field_mapping(url)
        
        # Save mappings to a file
        site_name = url.replace('https://', '').replace('http://', '').split('/')[0]
        mapping_file = f"config/{site_name}_mappings.json"
        
        import json
        with open(mapping_file, 'w') as f:
            json.dump(mappings, f, indent=2)
        
        print(f"✓ Mappings saved to {mapping_file}")
        print("You can now use these mappings for faster form filling")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        filler.close_driver()

def main():
    parser = argparse.ArgumentParser(description='Job Application Form Filler')
    parser.add_argument('--setup', action='store_true', 
                       help='Set up personal data configuration')
    parser.add_argument('--url', type=str, 
                       help='URL of web form to fill')
    parser.add_argument('--screen', action='store_true',
                       help='Fill form using screen detection')
    parser.add_argument('--create-mapping', type=str,
                       help='Create field mapping for a specific URL')
    parser.add_argument('--anthropic-key', type=str,
                       help='Anthropic API key for AI field matching')
    
    args = parser.parse_args()
    
    # Check if config directory exists
    os.makedirs('config', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    if args.setup:
        setup_personal_data()
    elif args.url:
        fill_web_form(args.url, args.anthropic_key)
    elif args.screen:
        fill_screen_form(args.anthropic_key)
    elif args.create_mapping:
        create_site_mapping(args.create_mapping, args.anthropic_key)
    else:
        # Interactive mode
        print("Job Application Form Filler")
        print("=" * 30)
        print("1. Set up personal data")
        print("2. Fill web form")
        print("3. Fill screen form")
        print("4. Create site mapping")
        print("5. Exit")
        
        while True:
            choice = input("\nSelect an option (1-5): ").strip()
            
            if choice == '1':
                setup_personal_data()
            elif choice == '2':
                url = input("Enter the URL: ").strip()
                if url:
                    fill_web_form(url, args.anthropic_key)
            elif choice == '3':
                fill_screen_form(args.anthropic_key)
            elif choice == '4':
                url = input("Enter the URL to create mapping for: ").strip()
                if url:
                    create_site_mapping(url, args.anthropic_key)
            elif choice == '5':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    main()