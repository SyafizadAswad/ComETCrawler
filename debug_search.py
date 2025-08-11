#!/usr/bin/env python3
"""
Debug script for COM-ET search interaction issues
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

def debug_search_interaction():
    print("COM-ET Search Debug Script")
    print("=" * 40)
    print()
    
    # Setup Chrome options (visible mode for debugging)
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--window-size=1920,1080")
    # Keep headless False for debugging
    # chrome_options.add_argument("--headless")
    
    try:
        # Initialize driver
        print("Initializing Chrome driver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to COM-ET website
        print("Navigating to COM-ET website...")
        driver.get("https://www.com-et.com/jp/")
        time.sleep(3)
        
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Find all input elements
        print("\nSearching for input elements...")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Found {len(inputs)} input elements")
        
        for i, inp in enumerate(inputs):
            try:
                input_type = inp.get_attribute("type")
                input_id = inp.get_attribute("id")
                input_name = inp.get_attribute("name")
                input_placeholder = inp.get_attribute("placeholder")
                is_displayed = inp.is_displayed()
                is_enabled = inp.is_enabled()
                
                print(f"Input {i+1}:")
                print(f"  Type: {input_type}")
                print(f"  ID: {input_id}")
                print(f"  Name: {input_name}")
                print(f"  Placeholder: {input_placeholder}")
                print(f"  Displayed: {is_displayed}")
                print(f"  Enabled: {is_enabled}")
                print()
                
                # Test if this looks like a search input
                if (input_type in ["text", "search"] and 
                    is_displayed and is_enabled and
                    (input_placeholder and "検索" in input_placeholder or
                     input_name and "search" in input_name.lower() or
                     input_id and "search" in input_id.lower())):
                    
                    print(f"*** POTENTIAL SEARCH INPUT FOUND: Input {i+1} ***")
                    
                    # Try to interact with it
                    try:
                        print("Attempting to interact with search input...")
                        
                        # Scroll to element
                        driver.execute_script("arguments[0].scrollIntoView(true);", inp)
                        time.sleep(1)
                        
                        # Clear and enter text
                        inp.clear()
                        time.sleep(0.5)
                        inp.send_keys("CS902B")
                        time.sleep(0.5)
                        
                        print("Successfully entered text!")
                        
                        # Try to submit
                        try:
                            inp.send_keys(Keys.RETURN)
                            print("Submitted with Enter key")
                        except:
                            print("Enter key failed, trying form submit...")
                            try:
                                driver.execute_script("arguments[0].form.submit();", inp)
                                print("Submitted with JavaScript")
                            except:
                                print("Form submit failed")
                        
                        time.sleep(5)
                        print(f"New URL: {driver.current_url}")
                        print(f"New title: {driver.title}")
                        
                    except Exception as e:
                        print(f"Interaction failed: {e}")
                        
            except Exception as e:
                print(f"Error analyzing input {i+1}: {e}")
        
        # Look for forms
        print("\nSearching for forms...")
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"Found {len(forms)} forms")
        
        for i, form in enumerate(forms):
            try:
                form_action = form.get_attribute("action")
                form_method = form.get_attribute("method")
                print(f"Form {i+1}: action={form_action}, method={form_method}")
            except:
                pass
        
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    debug_search_interaction() 