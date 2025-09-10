import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import List, Dict, Optional, Tuple
import os
from pathlib import Path

from .data_manager import DataManager
from .screen_analyzer import ScreenAnalyzer, FormField
from .field_matcher import FieldMatcher, FieldMatch

class FormFiller:
    def __init__(self, headless: bool = False, anthropic_api_key: Optional[str] = None):
        self.headless = headless
        self.driver = None
        self.data_manager = DataManager()
        self.screen_analyzer = ScreenAnalyzer()
        self.field_matcher = FieldMatcher(anthropic_api_key)
        
        # Safety settings
        self.auto_submit = False
        self.confirmation_required = True
        
        # Configure pyautogui safety
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
    
    def setup_driver(self):
        """Initialize Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def close_driver(self):
        """Clean up WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def fill_web_form(self, url: str, field_mappings: Optional[Dict[str, str]] = None) -> bool:
        """Fill a web form using Selenium"""
        if not self.driver:
            self.setup_driver()
        
        try:
            # Navigate to the page
            print(f"Navigating to: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            # If no mappings provided, try to auto-detect
            if not field_mappings:
                field_mappings = self._auto_detect_web_fields()
            
            if not field_mappings:
                print("No field mappings found. Cannot proceed.")
                return False
            
            # Fill each field
            filled_count = 0
            for field_selector, data_key in field_mappings.items():
                if self._fill_web_field(field_selector, data_key):
                    filled_count += 1
                    time.sleep(0.5)  # Small delay between fields
            
            print(f"Successfully filled {filled_count} fields")
            
            # Show confirmation if required
            if self.confirmation_required:
                return self._show_web_form_preview()
            
            return filled_count > 0
            
        except Exception as e:
            print(f"Error filling web form: {e}")
            return False
    
    def fill_screen_form(self, region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """Fill form fields detected on screen using computer vision"""
        try:
            # Capture screen
            print("Capturing screen...")
            self.screen_analyzer.capture_screen(region)
            
            # Detect form fields
            print("Detecting form fields...")
            fields = self.screen_analyzer.detect_form_fields()
            
            if not fields:
                print("No form fields detected on screen")
                return False
            
            print(f"Detected {len(fields)} form fields")
            
            # Match fields to data
            matches = self.field_matcher.match_fields(fields)
            
            # Show preview if confirmation required
            if self.confirmation_required:
                if not self._show_screen_form_preview(fields, matches):
                    return False
            
            # Fill fields
            filled_count = 0
            for field, match in zip(fields, matches):
                if match and self._fill_screen_field(field, match.data_key):
                    filled_count += 1
                    time.sleep(1)  # Delay between fields for safety
            
            print(f"Successfully filled {filled_count} fields")
            return filled_count > 0
            
        except Exception as e:
            print(f"Error filling screen form: {e}")
            return False
    
    def _auto_detect_web_fields(self) -> Dict[str, str]:
        """Auto-detect form fields on current web page"""
        mappings = {}
        
        try:
            # Find all input fields
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            
            all_fields = inputs + textareas + selects
            
            for field in all_fields:
                # Skip hidden fields
                if not field.is_displayed():
                    continue
                
                # Get field identifiers
                field_id = field.get_attribute('id')
                field_name = field.get_attribute('name')
                field_placeholder = field.get_attribute('placeholder')
                field_type = field.get_attribute('type')
                
                # Try to find associated label
                label_text = self._get_field_label(field)
                
                # Use the best identifier for the field
                field_identifier = field_id or field_name or f"xpath://*[@placeholder='{field_placeholder}']"
                
                if field_identifier:
                    # Try to match the field
                    field_text = label_text or field_placeholder or field_name or field_id or ''
                    match = self.field_matcher._pattern_field_matching(field_text, field_type or 'input')
                    
                    if match and match.confidence > 0.6:
                        mappings[field_identifier] = match.data_key
            
        except Exception as e:
            print(f"Error auto-detecting fields: {e}")
        
        return mappings
    
    def _get_field_label(self, field) -> Optional[str]:
        """Get label text for a form field"""
        try:
            # Check for explicit label
            field_id = field.get_attribute('id')
            if field_id:
                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
                if label:
                    return label.text.strip()
            
            # Check for parent label
            parent = field.find_element(By.XPATH, "./..")
            if parent.tag_name == 'label':
                return parent.text.strip()
            
            # Check for nearby text
            # This is a simplified version - could be improved
            siblings = field.find_elements(By.XPATH, "./preceding-sibling::*[1]")
            for sibling in siblings:
                if sibling.text.strip():
                    return sibling.text.strip()
                    
        except:
            pass
        
        return None
    
    def _fill_web_field(self, field_identifier: str, data_key: str) -> bool:
        """Fill a specific web form field"""
        try:
            # Get the data value
            value = self.data_manager.get_field_value(data_key)
            file_path = self.data_manager.get_file_path(data_key)
            
            if not value and not file_path:
                print(f"No data found for key: {data_key}")
                return False
            
            # Find the field
            field = None
            if field_identifier.startswith('xpath:'):
                xpath = field_identifier[6:]  # Remove 'xpath:' prefix
                field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
            else:
                # Try different locator strategies
                locator_strategies = [
                    (By.ID, field_identifier),
                    (By.NAME, field_identifier),
                    (By.CSS_SELECTOR, f"#{field_identifier}"),
                    (By.CSS_SELECTOR, f"[name='{field_identifier}']")
                ]
                
                for by, locator in locator_strategies:
                    try:
                        field = WebDriverWait(self.driver, 2).until(
                            EC.presence_of_element_located((by, locator))
                        )
                        break
                    except:
                        continue
            
            if not field:
                print(f"Could not find field: {field_identifier}")
                return False
            
            # Scroll to field
            self.driver.execute_script("arguments[0].scrollIntoView(true);", field)
            time.sleep(0.5)
            
            # Handle different field types
            field_type = field.get_attribute('type')
            tag_name = field.tag_name.lower()
            
            if file_path and field_type == 'file':
                # File upload
                field.send_keys(file_path)
            elif tag_name == 'select':
                # Dropdown selection
                select = Select(field)
                select.select_by_visible_text(value)
            elif field_type in ['checkbox', 'radio']:
                # Checkbox or radio button
                if value.lower() in ['true', 'yes', '1']:
                    if not field.is_selected():
                        field.click()
            else:
                # Regular text input
                field.clear()
                field.send_keys(value)
            
            print(f"Filled field {field_identifier} with {data_key}")
            return True
            
        except Exception as e:
            print(f"Error filling field {field_identifier}: {e}")
            return False
    
    def _fill_screen_field(self, field: FormField, data_key: str) -> bool:
        """Fill a screen-detected form field"""
        try:
            # Get the data value
            value = self.data_manager.get_field_value(data_key)
            file_path = self.data_manager.get_file_path(data_key)
            
            if not value and not file_path:
                print(f"No data found for key: {data_key}")
                return False
            
            # Click on the field
            click_x = field.x + field.width // 2
            click_y = field.y + field.height // 2
            
            pyautogui.click(click_x, click_y)
            time.sleep(0.5)
            
            # Handle file uploads
            if field.field_type == 'file' and file_path:
                # For file uploads, we might need to handle the file dialog
                time.sleep(1)  # Wait for file dialog
                pyautogui.typewrite(file_path)
                pyautogui.press('enter')
            else:
                # Clear field and type new value
                pyautogui.hotkey('ctrl', 'a')  # Select all
                pyautogui.typewrite(value)
            
            print(f"Filled screen field at ({click_x}, {click_y}) with {data_key}")
            return True
            
        except Exception as e:
            print(f"Error filling screen field: {e}")
            return False
    
    def _show_web_form_preview(self) -> bool:
        """Show preview of web form before submission"""
        print("\n" + "="*50)
        print("FORM PREVIEW")
        print("="*50)
        print("The form has been filled. Please review the page.")
        print("Would you like to:")
        print("1. Continue (submit the form)")
        print("2. Cancel (don't submit)")
        
        while True:
            choice = input("Enter your choice (1 or 2): ").strip()
            if choice == '1':
                return True
            elif choice == '2':
                return False
            else:
                print("Please enter 1 or 2")
    
    def _show_screen_form_preview(self, fields: List[FormField], matches: List[FieldMatch]) -> bool:
        """Show preview of screen form before filling"""
        print("\n" + "="*50)
        print("DETECTED FIELDS PREVIEW")
        print("="*50)
        
        for i, (field, match) in enumerate(zip(fields, matches)):
            if match:
                value = self.data_manager.get_field_value(match.data_key) or \
                       self.data_manager.get_file_path(match.data_key)
                print(f"{i+1}. {field.label or 'Unknown field'} -> {match.data_key}: {value}")
            else:
                print(f"{i+1}. {field.label or 'Unknown field'} -> No match found")
        
        print("\nWould you like to:")
        print("1. Continue (fill the form)")
        print("2. Cancel")
        
        while True:
            choice = input("Enter your choice (1 or 2): ").strip()
            if choice == '1':
                return True
            elif choice == '2':
                return False
            else:
                print("Please enter 1 or 2")
    
    def create_field_mapping(self, url: str) -> Dict[str, str]:
        """Interactive field mapping creation for a website"""
        if not self.driver:
            self.setup_driver()
        
        self.driver.get(url)
        time.sleep(3)
        
        # Auto-detect fields first
        auto_mappings = self._auto_detect_web_fields()
        
        print(f"\nAuto-detected {len(auto_mappings)} field mappings:")
        for field_id, data_key in auto_mappings.items():
            print(f"  {field_id} -> {data_key}")
        
        # Allow user to modify mappings
        print("\nWould you like to modify these mappings? (y/n)")
        if input().lower().startswith('y'):
            # Interactive mapping modification could be implemented here
            pass
        
        return auto_mappings