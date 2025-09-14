import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import time
import requests
from urllib.parse import urljoin, urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import urllib.request
import json
import config
from selenium.common.exceptions import TimeoutException, WebDriverException

class ComEtCrawler:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(config.GUI_TITLE)
        self.root.geometry(config.GUI_SIZE)
        self.root.configure(bg=config.GUI_BG_COLOR)
        
        # Variables
        self.product_id = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready to search...")
        self.progress_var = tk.DoubleVar()
        self.is_searching = False
        self.log_file_path = None
        
        # Load color codes
        self.color_codes = self.load_color_codes()
        
        # Output directory
        self.output_dir = config.OUTPUT_DIR
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.setup_gui()
    
    def load_color_codes(self):
        """Load color codes from the JSON file"""
        try:
            color_code_file = os.path.join(os.path.dirname(__file__), 'colorcode.json')
            with open(color_code_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.log_and_update(f"Error loading color codes: {str(e)}")
            return {}
    
    def get_color_name_from_product_id(self, product_id):
        """Extract color name from product ID using color codes mapping"""
        try:
            if not product_id or not self.color_codes:
                return ""
            
            # Look for color codes in the product ID
            # Common patterns: #SC1, #54R, #1, etc.
            color_patterns = [
                r'#([A-Z0-9]+)',  # Matches #SC1, #54R, etc.
                r'([A-Z0-9]+)$'   # Matches color codes at the end
            ]
            
            for pattern in color_patterns:
                matches = re.findall(pattern, product_id)
                for match in matches:
                    color_code = f"#{match}"
                    if color_code in self.color_codes:
                        return self.color_codes[color_code]
            
            return ""
        except Exception as e:
            self.log_and_update(f"Error extracting color name from {product_id}: {str(e)}")
            return ""
    
    def format_product_id_with_color(self, product_id):
        """Format product ID with color name if available"""
        try:
            color_name = self.get_color_name_from_product_id(product_id)
            if color_name:
                return f"{product_id}({color_name})"
            else:
                return product_id
        except Exception as e:
            self.log_and_update(f"Error formatting product ID {product_id}: {str(e)}")
            return product_id
        
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text=config.GUI_TITLE, 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Product ID input
        ttk.Label(main_frame, text="Product ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.product_entry = ttk.Entry(main_frame, textvariable=self.product_id, width=40)
        self.product_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        
        # Search button
        self.search_button = ttk.Button(main_frame, text="Search & Download", 
                                       command=self.start_search)
        self.search_button.grid(row=1, column=2, pady=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                              pady=10, padx=(0, 0))
        
        # Status label
        self.status_label = ttk.Label(main_frame, textvariable=self.status_text, 
                                     font=("Arial", 10))
        self.status_label.grid(row=3, column=0, columnspan=3, pady=5)
        
        # Results text area
        ttk.Label(main_frame, text="Search Results:").grid(row=4, column=0, 
                                                          sticky=tk.W, pady=(20, 5))
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.results_text = tk.Text(text_frame, height=15, width=80, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure main frame row weights
        main_frame.rowconfigure(5, weight=1)
        
        # Bind Enter key to search
        self.product_entry.bind('<Return>', lambda e: self.start_search())
        
    def start_search(self):
        if self.is_searching:
            return
            
        product_id = self.product_id.get().strip()
        if not product_id:
            messagebox.showerror("Error", "Please enter a product ID")
            return
            
        self.is_searching = True
        self.search_button.config(state='disabled')
        self.progress_var.set(0)
        self.status_text.set("Initializing browser...")
        self.results_text.delete(1.0, tk.END)

        # Set up log file path
        self.log_file_path = os.path.join(self.output_dir, f"log_{product_id}_{int(time.time())}.txt")
        with open(self.log_file_path, "w", encoding="utf-8") as log_file:
            log_file.write(f"--- Starting search for product ID: {product_id} at {time.ctime()} ---\n\n")
        
        # Start search in separate thread
        thread = threading.Thread(target=self.perform_search, args=(product_id,))
        thread.daemon = True
        thread.start()
    
    def log_and_update(self, message):
        """Updates the GUI and logs the message to a file."""
        self.update_results(f"{message}\n")
        try:
            if self.log_file_path:
                with open(self.log_file_path, "a", encoding="utf-8") as log_file:
                    log_file.write(f"[{time.ctime()}] {message}\n")
        except Exception as e:
            self.update_results(f"Error writing to log file: {e}\n")

    def perform_search(self, product_id):
        try:
            # Setup Chrome options
            chrome_options = Options()
            for option, value in config.BROWSER_OPTIONS.items():
                if option == "headless" and value:
                    chrome_options.add_argument("--headless")
                elif option == "no_sandbox" and value:
                    chrome_options.add_argument("--no-sandbox")
                elif option == "disable_dev_shm_usage" and value:
                    chrome_options.add_argument("--disable-dev-shm-usage")
                elif option == "disable_gpu" and value:
                    chrome_options.add_argument("--disable-gpu")
                elif option == "window_size":
                    chrome_options.add_argument(f"--window-size={value}")
                elif option == "user_agent":
                    chrome_options.add_argument(f"--user-agent={value}")
                elif option == "disable_extensions" and value:
                    chrome_options.add_argument("--disable-extensions")
                elif option == "disable_plugins" and value:
                    chrome_options.add_argument("--disable-plugins")
                elif option == "disable_web_security" and value:
                    chrome_options.add_argument("--disable-web-security")
                elif option == "allow_running_insecure_content" and value:
                    chrome_options.add_argument("--allow-running-insecure-content")
                elif option == "disable_background_networking" and value:
                    chrome_options.add_argument("--disable-background-networking")
                elif option == "disable_background_timer_throttling" and value:
                    chrome_options.add_argument("--disable-background-timer-throttling")
                elif option == "disable_client_side_phishing_detection" and value:
                    chrome_options.add_argument("--disable-client-side-phishing-detection")
                elif option == "disable_default_apps" and value:
                    chrome_options.add_argument("--disable-default-apps")
                elif option == "disable_hang_monitor" and value:
                    chrome_options.add_argument("--disable-hang-monitor")
                elif option == "disable_prompt_on_repost" and value:
                    chrome_options.add_argument("--disable-prompt-on-repost")
                elif option == "disable_sync" and value:
                    chrome_options.add_argument("--disable-sync")
                elif option == "metrics_recording_only" and value:
                    chrome_options.add_argument("--metrics-recording-only")
                elif option == "no_first_run" and value:
                    chrome_options.add_argument("--no-first-run")
                elif option == "safeBrowse_disable_auto_update" and value:
                    chrome_options.add_argument("--safeBrowse-disable-auto-update")
                elif option == "disable_software_rasterizer" and value:
                    chrome_options.add_argument("--disable-software-rasterizer")
            
            # Initialize driver with comprehensive error handling for Windows
            driver = None
            error_messages = []
            
            # Method 1: Try with ChromeDriverManager
            try:
                self.log_and_update("Initializing Chrome driver (method 1)...")
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                self.log_and_update("Chrome driver initialized successfully!")
            except Exception as e1:
                error_messages.append(f"Method 1 failed: {str(e1)}")
                self.log_and_update(f"Method 1 failed: {str(e1)}")
                
                # Method 2: Try with ChromeService
                try:
                    self.log_and_update("Trying alternative Chrome driver initialization...")
                    from selenium.webdriver.chrome.service import Service as ChromeService
                    from webdriver_manager.chrome import ChromeDriverManager
                    
                    service = ChromeService(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    self.log_and_update("Chrome driver initialized successfully!")
                except Exception as e2:
                    error_messages.append(f"Method 2 failed: {str(e2)}")
                    self.log_and_update(f"Method 2 failed: {str(e2)}")
                    
                    # Method 3: Try with minimal options
                    try:
                        self.log_and_update("Trying with minimal Chrome options...")
                        minimal_options = Options()
                        minimal_options.add_argument("--headless")
                        minimal_options.add_argument("--no-sandbox")
                        minimal_options.add_argument("--disable-dev-shm_usage")
                        minimal_options.add_argument("--disable-gpu")
                        minimal_options.add_argument("--disable-extensions")
                        minimal_options.add_argument("--disable-plugins")
                        
                        service = Service(ChromeDriverManager().install())
                        driver = webdriver.Chrome(service=service, options=minimal_options)
                        self.log_and_update("Chrome driver initialized with minimal options!")
                    except Exception as e3:
                        error_messages.append(f"Method 3 failed: {str(e3)}")
                        self.log_and_update(f"Method 3 failed: {str(e3)}")
                        
                        # Method 4: Try without headless mode
                        try:
                            self.log_and_update("Trying without headless mode...")
                            visible_options = Options()
                            visible_options.add_argument("--no-sandbox")
                            visible_options.add_argument("--disable-dev-shm_usage")
                            visible_options.add_argument("--disable-gpu")
                            visible_options.add_argument("--disable-extensions")
                            visible_options.add_argument("--disable-plugins")
                            # Remove headless mode for debugging
                            
                            service = Service(ChromeDriverManager().install())
                            driver = webdriver.Chrome(service=service, options=visible_options)
                            self.log_and_update("Chrome driver initialized in visible mode!")
                        except Exception as e4:
                            error_messages.append(f"Method 4 failed: {str(e4)}")
                            self.log_and_update(f"Method 4 failed: {str(e4)}")
                            
                            # Final attempt: Try with system PATH
                            try:
                                self.log_and_update("Trying with system ChromeDriver...")
                                driver = webdriver.Chrome(options=chrome_options)
                                self.log_and_update("Chrome driver initialized from system PATH!")
                            except Exception as e5:
                                error_messages.append(f"Method 5 failed: {str(e5)}")
                                self.log_and_update(f"Method 5 failed: {str(e5)}")
                                raise Exception(f"All Chrome driver initialization methods failed. Errors: {'; '.join(error_messages)}. Please run 'python troubleshoot_chrome.py' for detailed diagnostics.")
            
            if driver is None:
                self.log_and_update("Failed to initialize Chrome driver after all attempts.")
                raise Exception("Failed to initialize Chrome driver after all attempts.")
            
            try:
                self.log_and_update("Navigating to COM-ET website...")
                driver.get(config.WEBSITE_URL)
                
                # Wait for page to load
                try:
                    WebDriverWait(driver, config.SEARCH_TIMEOUT).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    self.log_and_update("Page loaded successfully.")
                except TimeoutException:
                    self.log_and_update("Timeout waiting for page to load.")
                
                self.log_and_update("Looking for search bar...")
                
                # Use the specific CSS selector provided by the user
                search_selector = "div.searchArea.incSearchOptions input#searchBox"
                search_input = None
                
                try:
                    search_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, search_selector))
                    )
                except Exception as e:
                    self.log_and_update(f"Could not find search input field with selector '{search_selector}': {str(e)}")
                    raise Exception(f"Could not find search input field with selector '{search_selector}': {str(e)}")
                
                if not (search_input and search_input.is_displayed() and search_input.is_enabled()):
                    self.log_and_update("Search input field is not visible or enabled.")
                    raise Exception("Search input field is not visible or enabled.")
                
                self.log_and_update(f"Entering product ID: {product_id}")
                
                # Wait for element to be interactable
                try:
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, search_selector))
                    )
                    self.log_and_update("Search input field is clickable.")
                except:
                    self.log_and_update("Search input field is not clickable, trying simpler approach.")
                    # If that fails, try a simpler approach
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.TAG_NAME, "input"))
                        )
                    except:
                        pass
                
                # Clear and enter product ID with better interaction
                try:
                    self.log_and_update("Attempting to send keys to search field...")
                    # Scroll to element to ensure it's visible
                    driver.execute_script("arguments[0].scrollIntoView(true);", search_input)
                    time.sleep(1)
                    
                    # Clear the field
                    search_input.clear()
                    time.sleep(0.5)
                    
                    # Enter the product ID
                    search_input.send_keys(product_id)
                    time.sleep(0.5)
                    
                    # Submit the search
                    search_input.send_keys(Keys.RETURN)
                    self.log_and_update("Submitted search by pressing RETURN.")
                except Exception as e:
                    # Fallback: try JavaScript interaction
                    self.log_and_update("Failed to send keys. Trying JavaScript interaction...")
                    try:
                        driver.execute_script(f"arguments[0].value = '{product_id}';", search_input)
                        driver.execute_script("arguments[0].form.submit();", search_input)
                        self.log_and_update("Submitted search via JavaScript.")
                    except:
                        # Last resort: try to find and click a search button
                        self.log_and_update("JavaScript submission failed. Trying to find a search button.")
                        try:
                            search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .search-button, .btn-button")
                            search_button.click()
                            self.log_and_update("Submitted search by clicking a button.")
                        except:
                            self.log_and_update(f"Could not interact with search field: {str(e)}")
                            raise Exception(f"Could not interact with search field: {str(e)}")
                
                # Wait for search results to load
                self.log_and_update("Waiting for search results to load...")
                time.sleep(5)  # Give more time for dynamic content
                
                # Wait for search results to be visible
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    self.log_and_update("Search results page body loaded.")
                except:
                    self.log_and_update("Timeout waiting for search results page body. Proceeding anyway.")
                
                # Check if we're still on the search page (search might have failed)
                current_url = driver.current_url
                if "search" not in current_url.lower() and "result" not in current_url.lower():
                    self.log_and_update("Search may have failed. URL does not indicate a search result page. Trying alternative method...")
                    # Try alternative search method using JavaScript
                    try:
                        # Try to find and fill search form using JavaScript
                        js_code = f"""
                        var inputs = document.querySelectorAll('input[type="text"], input[type="search"]');
                        for (var i = 0; i < inputs.length; i++) {{
                            if (inputs[i].offsetParent !== null) {{
                                inputs[i].value = '{product_id}';
                                inputs[i].focus();
                                break;
                            }}
                        }}
                        """
                        driver.execute_script(js_code)
                        time.sleep(1)
                        self.log_and_update("Filled search form with JavaScript.")
                        
                        # Try to submit the form
                        submit_js = """
                        var forms = document.querySelectorAll('form');
                        for (var i = 0; i < forms.length; i++) {
                            var inputs = forms[i].querySelectorAll('input[type="text"], input[type="search"]');
                            if (inputs.length > 0) {
                                forms[i].submit();
                                break;
                            }
                        }
                        """
                        driver.execute_script(submit_js)
                        time.sleep(5)
                        self.log_and_update("Submitted search form with JavaScript.")
                    except Exception as e:
                        self.log_and_update(f"Alternative search method with JavaScript failed: {str(e)}")
                
                # Process all result pages
                self.process_search_results_across_pages(driver, product_id)
                
            finally:
                if driver:
                    driver.quit()
                self.log_and_update("Browser closed.")
                
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.log_and_update(f"FATAL ERROR occurred: {str(e)}")
        finally:
            self.is_searching = False
            self.search_button.config(state='normal')
    
    def ensure_on_search_results_page(self, driver):
        """Ensure we're on the search results page before processing products."""
        try:
            current_url = driver.current_url
            # Check if we're on a search results page
            if "item_search" not in current_url and "search" not in current_url:
                self.log_and_update("    Not on search results page, attempting to return...")
                # Try to go back to the search results
                driver.back()
                time.sleep(2)
                
                # If still not on search results, try to navigate to the original search URL
                if "item_search" not in driver.current_url:
                    self.log_and_update("    Attempting to return to search results page...")
                    # You might need to store the original search URL and navigate back to it
                    # For now, we'll just log the issue
                    self.log_and_update(f"    Current URL: {driver.current_url}")
        except Exception as e:
            self.log_and_update(f"    Error ensuring on search results page: {str(e)}")

    def process_search_results_across_pages(self, driver, search_product_id):
        """Iterate all result pages, process products, and paginate via 次へ until done."""
        total_downloaded = 0
        page_index = 1
        seen_product_ids = set()

        while True:
            try:
                self.log_and_update(f"Analyzing search results page {page_index} for product containers...")
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                    )
                except TimeoutException:
                    self.log_and_update("Timeout waiting for page body; continuing anyway.")

                # Locate product containers
                product_containers = []
                container_selectors = [
                    "table.productTable tbody tr",
                    "table.productTable tr",
                    ".product",
                    ".item",
                    ".result",
                    "[class*='product']",
                    "[class*='item']",
                    "[class*='result']",
                    "div[class*='product']",
                    "div[class*='item']",
                    "li[class*='product']",
                    "li[class*='item']"
                ]

                for selector in container_selectors:
                    try:
                        containers = driver.find_elements(By.CSS_SELECTOR, selector)
                        if containers:
                            filtered = []
                            for container in containers:
                                try:
                                    text_value = container.text
                                    if any(k in text_value for k in ['品番', '商品名', '商品図', 'Product']):
                                        filtered.append(container)
                                except Exception:
                                    continue
                            if filtered:
                                product_containers = filtered
                                self.log_and_update(f"Found {len(filtered)} product containers using selector: {selector}")
                                break
                    except Exception as e:
                        self.log_and_update(f"Selector {selector} failed: {e}")

                if not product_containers:
                    self.log_and_update("No product containers with primary selectors. Trying broader search...")
                    try:
                        all_elements = driver.find_elements(By.CSS_SELECTOR, "div, li, section")
                        for element in all_elements:
                            try:
                                et = element.text
                                if '品番' in et and ('商品名' in et or '商品図' in et):
                                    product_containers.append(element)
                            except Exception:
                                continue
                    except Exception as e:
                        self.log_and_update(f"Broader search failed: {e}")

                self.log_and_update(f"Page {page_index}: {len(product_containers)} potential product containers found")

                # Extract and process products for this page
                products_data = []
                for i, container in enumerate(product_containers):
                    try:
                        self.log_and_update(f"Extracting info from container {i+1}/{len(product_containers)} on page {page_index}")
                        product_info = self.extract_product_info(container, driver)
                        if product_info and product_info['product_id'] not in seen_product_ids:
                            products_data.append(product_info)
                            seen_product_ids.add(product_info['product_id'])
                            self.log_and_update(f"Queued product: {product_info['product_id']} - {product_info['product_name']}")
                        elif product_info:
                            self.log_and_update(f"Skipping duplicate product: {product_info['product_id']}")
                    except Exception as e:
                        self.log_and_update(f"Error extracting container on page {page_index}: {str(e)}")

                if not products_data:
                    self.log_and_update("No products extracted; trying fallback detection on this page...")
                    fallback_products = self.fallback_product_detection(driver)
                    for product in fallback_products:
                        if product['product_id'] not in seen_product_ids:
                            products_data.append(product)
                            seen_product_ids.add(product['product_id'])

                if products_data:
                    self.log_and_update(f"Processing {len(products_data)} products on page {page_index}...")
                else:
                    self.log_and_update(f"No products to process on page {page_index}.")

                # Process each product, including color variations
                for i, product in enumerate(products_data):
                    try:
                        self.update_status(f"Processing (page {page_index}) {product['product_id']}")
                        
                        # Check if this product has color variations
                        color_variations = self.process_color_variations(driver, product)
                        
                        if color_variations:
                            self.log_and_update(f"Found {len(color_variations)} color variations for {product['product_id']}")
                            # Process each color variation
                            for color_product in color_variations:
                                if color_product['product_id'] not in seen_product_ids:
                                    seen_product_ids.add(color_product['product_id'])
                                    if self.process_product_diagrams(driver, color_product):
                                        total_downloaded += 1
                        else:
                            # Process the original product if no color variations
                            if self.process_product_diagrams(driver, product):
                                total_downloaded += 1
                                
                    except Exception as e:
                        self.log_and_update(f"Error processing {product.get('product_id', 'unknown')} on page {page_index}: {str(e)}")

                # Pagination: click 次へ (class="next") if present
                try:
                    next_button = None
                    try:
                        # Prefer within section.searchInfo
                        next_button = driver.find_element(By.CSS_SELECTOR, "section.searchInfo ul.pageing a.next")
                    except Exception:
                        # Fallback to any pagination next
                        elems = driver.find_elements(By.CSS_SELECTOR, "ul.pageing a.next")
                        if elems:
                            next_button = elems[0]

                    if next_button and next_button.is_displayed() and next_button.is_enabled():
                        self.log_and_update("Next page detected. Navigating to the next page (次へ)...")
                        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                        time.sleep(0.5)
                        next_button.click()
                        # wait for page navigation by checking URL or body refresh
                        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
                        time.sleep(2)
                        page_index += 1
                        continue
                    else:
                        self.log_and_update("No further pages detected. Finishing.")
                        break
                except Exception as e:
                    self.log_and_update(f"Pagination check/click failed or no more pages: {str(e)}")
                    break

            except Exception as e:
                self.log_and_update(f"Unexpected error while processing pages: {str(e)}")
                break

        self.progress_var.set(100)
        self.update_status(f"Search completed across pages. Downloads completed for {total_downloaded} products.")
        self.log_and_update(f"Search completed across pages. Downloads completed for {total_downloaded} products.")

    def process_color_variations(self, driver, product):
        """Process color variations for a product by clicking the color link and extracting all variants"""
        try:
            # Look for the color link within the product container
            color_link = None
            try:
                # Find the productColorLink within the product container
                color_link = product['container'].find_element(By.CSS_SELECTOR, ".productColorLink a")
                self.log_and_update(f"  Found color variation link for {product['product_id']}")
            except Exception as e:
                self.log_and_update(f"  No color variation link found for {product['product_id']}: {str(e)}")
                return []
            
            if not color_link:
                return []
            
            # Store the original window handle
            original_window = driver.current_window_handle
            
            try:
                # Click the color link
                self.log_and_update(f"  Clicking color variation link for {product['product_id']}")
                driver.execute_script("arguments[0].scrollIntoView(true);", color_link)
                time.sleep(1)
                
                # Check if a new window/tab opens
                existing_handles = set(driver.window_handles)
                color_link.click()
                time.sleep(3)
                
                new_handles = set(driver.window_handles) - existing_handles
                if new_handles:
                    # Switch to the new window
                    new_window = list(new_handles)[0]
                    driver.switch_to.window(new_window)
                    self.log_and_update(f"  Switched to color variations window for {product['product_id']}")
                else:
                    self.log_and_update(f"  Color variations opened in same window for {product['product_id']}")
                
                # Wait for the color variations page to load
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                    )
                except TimeoutException:
                    self.log_and_update(f"  Timeout waiting for color variations page to load for {product['product_id']}")
                
                # Extract all color variation products
                color_products = self.extract_color_variation_products(driver, product)
                
                # Close the color variations window and return to original
                if new_handles:
                    driver.close()
                    driver.switch_to.window(original_window)
                    self.log_and_update(f"  Closed color variations window and returned to original for {product['product_id']}")
                
                return color_products
                
            except Exception as e:
                self.log_and_update(f"  Error processing color variations for {product['product_id']}: {str(e)}")
                # Try to return to original window
                try:
                    if len(driver.window_handles) > 1 and driver.current_window_handle != original_window:
                        driver.close()
                        driver.switch_to.window(original_window)
                except:
                    pass
                return []
                
        except Exception as e:
            self.log_and_update(f"  Error in process_color_variations for {product['product_id']}: {str(e)}")
            return []

    def extract_color_variation_products(self, driver, original_product):
        """Extract all color variation products from the color variations page"""
        try:
            self.log_and_update(f"    Extracting color variation products...")
            color_products = []
            
            # Look for product containers on the color variations page
            product_containers = []
            container_selectors = [
                "table.productTable tbody tr",
                "table.productTable tr",
                ".product",
                ".item",
                ".result",
                "[class*='product']",
                "[class*='item']",
                "[class*='result']"
            ]
            
            for selector in container_selectors:
                try:
                    containers = driver.find_elements(By.CSS_SELECTOR, selector)
                    if containers:
                        filtered = []
                        for container in containers:
                            try:
                                text_value = container.text
                                if any(k in text_value for k in ['品番', '商品名', '商品図', 'Product']):
                                    filtered.append(container)
                            except Exception:
                                continue
                        if filtered:
                            product_containers = filtered
                            self.log_and_update(f"    Found {len(filtered)} color variation containers using selector: {selector}")
                            break
                except Exception as e:
                    self.log_and_update(f"    Selector {selector} failed: {e}")
            
            if not product_containers:
                self.log_and_update(f"    No color variation containers found")
                return []
            
            # Extract product info for each color variation
            for i, container in enumerate(product_containers):
                try:
                    self.log_and_update(f"    Extracting color variation {i+1}/{len(product_containers)}")
                    color_product_info = self.extract_product_info(container, driver)
                    
                    if color_product_info:
                        # Use the original product's name and series as base
                        color_product_info['product_name'] = original_product.get('product_name', '')
                        color_product_info['series'] = original_product.get('series', '')
                        color_products.append(color_product_info)
                        self.log_and_update(f"    Extracted color variation: {color_product_info['product_id']}")
                    
                except Exception as e:
                    self.log_and_update(f"    Error extracting color variation {i+1}: {str(e)}")
                    continue
            
            self.log_and_update(f"    Successfully extracted {len(color_products)} color variations")
            return color_products
            
        except Exception as e:
            self.log_and_update(f"    Error extracting color variation products: {str(e)}")
            return []

    def extract_product_info(self, container, driver):
        """
        Extract product information from a container element,
        prioritizing diagram links that precisely match the product_id.
        """
        self.log_and_update("  Starting to extract product info...")
        try:
            product_id = None
            product_name = "Unknown Product"
            diagram_link = None
            specs_link = None
            bunkaizu_link = None
            product_images = [] 
            diagram_href = None
            specs_href = None
            bunkaizu_href = None
            
            # Find the '品番' (product ID) link
            try:
                self.log_and_update("  Attempting to find 品番 link...")
                # Find the dt with '品番' text
                hinban_dt = container.find_element(By.XPATH, ".//dt[contains(text(), '品番')]")
                # Find the sibling dd element
                hinban_dd = hinban_dt.find_element(By.XPATH, "./following-sibling::dd")
                # Find the link within the dd element
                product_id_link = hinban_dd.find_element(By.TAG_NAME, "a")
                product_id = product_id_link.text.strip()
                self.log_and_update(f"  Found product ID: {product_id}")
            except Exception as e:
                self.log_and_update(f"  Error finding 品番 link: {str(e)}")
                return None
            
            # Find the '商品名' (product name)
            try:
                self.log_and_update("  Attempting to find 商品名...")
                product_name_dd = container.find_element(By.XPATH, ".//dt[contains(text(), '商品名')]/following-sibling::dd")
                product_name = product_name_dd.text.strip()
                self.log_and_update(f"  Found product name: {product_name}")
            except:
                self.log_and_update("  Product name not found.")
                pass
            
            if not product_id:
                self.log_and_update("  Product ID is empty, skipping this container.")
                return None

            # Skip discontinued items (販売終了)
            try:
                self.log_and_update("  Checking 希望小売価格 for discontinued status...")
                price_dd = container.find_element(
                    By.XPATH,
                    ".//dt[contains(text(), '希望小売価格')]/following-sibling::dd[contains(@class, 'price')]"
                )
                price_text = price_dd.text.strip()
                self.log_and_update(f"  希望小売価格 text: {price_text}")
                if "販売終了" in price_text:
                    self.log_and_update("  Item marked as 販売終了. Skipping this item.")
                    return None
            except Exception as e:
                self.log_and_update(f"  Could not determine discontinued status: {str(e)}")
            
            all_links_in_container = container.find_elements(By.TAG_NAME, "a")
            self.log_and_update(f"  Found {len(all_links_in_container)} links in total within the container.")
            
            # --- Diagram Link Selection Logic ---
            self.log_and_update("  Searching for Diagram link (商品図)...")
            found_exact_diagram = False
            for link in all_links_in_container:
                href = link.get_attribute('href')
                link_text = link.text.strip()
                if '商品図' in link_text and href:
                    self.log_and_update(f"    Found a link with '商品図' text: {link_text} ({href})")
                    parsed_path = urlparse(href).path
                    filename = os.path.basename(parsed_path)
                    
                    if re.search(r'\b' + re.escape(product_id) + r'\b', filename, re.IGNORECASE):
                        diagram_link = link
                        diagram_href = href
                        found_exact_diagram = True
                        self.log_and_update(f"    Found exact diagram match for product ID: {diagram_href}")
                        break
            
            if not found_exact_diagram:
                self.log_and_update("    No exact diagram match found. Falling back to general search.")
                for link in all_links_in_container:
                    href = link.get_attribute('href')
                    link_text = link.text.strip()
                    if '商品図' in link_text:
                        diagram_link = link
                        diagram_href = href
                        self.log_and_update(f"    Found general diagram link: {diagram_href}")
                        break
                    elif href and ('diagram' in href.lower() or 'drawing' in href.lower()):
                        if not diagram_link:
                            diagram_link = link
                            diagram_href = href
                            self.log_and_update(f"    Found fallback diagram link by keyword: {diagram_href}")

            # --- Specifications Link Selection Logic ---
            self.log_and_update("  Searching for Specifications link (仕様一覧)...")
            specs_links = []
            
            # Method 1: Look for 仕様一覧 links in the productLabels section
            try:
                specs_links = container.find_elements(By.CSS_SELECTOR, "ul.productLabels a")
                self.log_and_update(f"    Method 1 found {len(specs_links)} potential links.")
            except Exception as e:
                self.log_and_update(f"    Method 1 (CSS Selector) failed: {str(e)}")
            
            # Fallback if Method 1 fails
            if not specs_links:
                try:
                    # If we're in a td element, look in the entire tr
                    if container.tag_name == "td":
                        parent_tr = container.find_element(By.XPATH, "./..")
                        specs_links = parent_tr.find_elements(By.CSS_SELECTOR, "ul.productLabels a")
                        self.log_and_update(f"    Method 1 fallback on parent TR found {len(specs_links)} links.")
                    # If we're in a th element, look in the sibling td
                    elif container.tag_name == "th":
                        parent_tr = container.find_element(By.XPATH, "./..")
                        td_element = parent_tr.find_element(By.TAG_NAME, "td")
                        specs_links = td_element.find_elements(By.CSS_SELECTOR, "ul.productLabels a")
                        self.log_and_update(f"    Method 1 fallback on sibling TD found {len(specs_links)} links.")
                except Exception as e:
                    self.log_and_update(f"    Method 1 fallback failed: {str(e)}")

            found_specs_link_to_use = False
            for link in specs_links:
                href = link.get_attribute('href')
                link_text = link.text.strip()
                if '仕様一覧' in link_text and href:
                    self.log_and_update(f"    Found a link with '仕様一覧' text: {link_text} ({href})")
                    
                    # New logic: Proceed with extraction if the link matches the base URL pattern, without strict hinban validation
                    if "https://www.com-et.com/jp/item_view_spec/" in href:
                        specs_link = link
                        specs_href = href
                        found_specs_link_to_use = True
                        self.log_and_update(f"    Link URL matches the specifications view pattern. Specs link found: {specs_href}")
                        break
                    else:
                        self.log_and_update(f"    Link found, but URL does not match the expected pattern. Skipping validation: {href}")
            
            if not found_specs_link_to_use:
                self.log_and_update("  No valid Specifications link found for this product.")

            # --- 分解図 (Exploded Diagram) Link Selection Logic ---
            self.log_and_update("  Searching for 分解図 link...")
            try:
                bunkaizu_candidates = container.find_elements(By.XPATH, ".//a[contains(., '分解図')]")
                for link in bunkaizu_candidates:
                    href = link.get_attribute('href')
                    if href:
                        bunkaizu_link = link
                        bunkaizu_href = href
                        self.log_and_update(f"    Found 分解図 link: {bunkaizu_href}")
                        break
            except Exception as e:
                self.log_and_update(f"    Error finding 分解図 link: {str(e)}")
            
            # --- Product Images Selection Logic ---
            self.log_and_update("  Searching for product images...")
            product_images = []
            
            # Find all image links based on the URL pattern, regardless of alt text.
            image_links = container.find_elements(By.CSS_SELECTOR, "a[href*='search.toto.jp/img/']")
            self.log_and_update(f"    Found {len(image_links)} image links in container.")
            
            if not image_links:
                try:
                    # If no images found in current container, try parent/sibling.
                    if container.tag_name == "td":
                        parent_tr = container.find_element(By.XPATH, "./..")
                        th_element = parent_tr.find_element(By.TAG_NAME, "th")
                        image_links = th_element.find_elements(By.CSS_SELECTOR, "a[href*='search.toto.jp/img/']")
                        self.log_and_update(f"    Found {len(image_links)} image links in parent/sibling.")
                    elif container.tag_name == "th":
                        image_links = container.find_elements(By.CSS_SELECTOR, "a[href*='search.toto.jp/img/']")
                except Exception as e:
                    self.log_and_update(f"    Error finding images in parent/sibling: {str(e)}")
            
            for link in image_links:
                try:
                    href = link.get_attribute('href')
                    alt_text = link.get_attribute('alt') or ""
                    
                    # New logic: Don't strictly validate alt text. Just assume the link is for this product.
                    image_info = {
                        'href': href,
                        'alt': alt_text,
                        'element': link
                    }
                    product_images.append(image_info)
                    self.log_and_update(f"    Collected image link: {href}")
                except Exception as e:
                    self.log_and_update(f"    Error processing image link: {str(e)}")
                    continue
            
            self.log_and_update("  Finished extracting product info.")
            return {
                'product_id': product_id,
                'product_name': product_name,
                'container': container,
                'diagram_link': diagram_link,
                'diagram_href': diagram_href,
                'bunkaizu_link': bunkaizu_link,
                'bunkaizu_href': bunkaizu_href,
                'specs_link': specs_link,
                'specs_href': specs_href,
                'product_images': product_images, # List of images to download
                'container_text': container.text # Use container.text to get all text
            }
            
        except Exception as e:
            self.log_and_update(f"  Error extracting product info: {str(e)}")
            return None

    def fallback_product_detection(self, driver):
        """Fallback method to detect products when containers are not found"""
        self.log_and_update("  Starting fallback product detection...")
        products_data = []
        try:
            # Look for any 商品図 links on the page
            diagram_links = driver.find_elements(By.XPATH, "//a[contains(text(), '商品図')]")
            self.log_and_update(f"  Fallback: Found {len(diagram_links)} '商品図' links.")
            
            for i, link in enumerate(diagram_links):
                try:
                    # Try to find product ID in nearby text
                    parent = link.find_element(By.XPATH, "./..")
                    parent_text = parent.text
                    
                    import re
                    product_id_match = re.search(r'◆([A-Z0-9]+)', parent_text)
                    if product_id_match:
                        product_id = product_id_match.group(1)
                        self.log_and_update(f"  Fallback: Detected product ID '{product_id}' from nearby text.")
                    else:
                        product_id = f"Product_{i+1}"
                        self.log_and_update(f"  Fallback: Could not detect product ID from text, using generic ID '{product_id}'.")
                    
                    products_data.append({
                        'product_id': product_id,
                        'product_name': f"Product {i+1}",
                        'diagram_link': link,
                        'container_text': parent_text
                    })
                    
                except Exception as e:
                    self.log_and_update(f"  Error in fallback detection: {str(e)}")
                    
        except Exception as e:
            self.log_and_update(f"  Fallback detection failed: {str(e)}")
        
        return products_data

    def process_product_diagrams(self, driver, product):
        """Process diagrams and specifications for a specific product in sequence."""
        self.log_and_update(f"\n--- Processing Product: {product['product_id']} ---\n")
        downloaded_something = False
        
        try:
            # Store the original window handle to ensure we return to the search results page
            original_window = driver.current_window_handle
            
            # Create directory for this product
            product_dir = os.path.join(self.output_dir, product['product_id'])
            diagram_dir = os.path.join(product_dir, config.DIAGRAM_FOLDER_NAME)
            os.makedirs(diagram_dir, exist_ok=True)
            self.log_and_update(f"  Created product directory: {product_dir}")
            
            # 1. Download Product Images (maximum 2 per product ID)
            if product.get('product_images'):
                self.log_and_update(f"  Image: Attempting to download {min(2, len(product['product_images']))} images for {product['product_id']}...")
                downloaded_image_count = 0
                for image_info in product['product_images']:
                    if downloaded_image_count >= 2:
                        self.log_and_update("  Reached maximum of 2 product images, skipping further images.")
                        break
                    
                    try:
                        if self.download_product_image(driver, image_info, diagram_dir):
                            downloaded_something = True
                            downloaded_image_count += 1
                    except Exception as e:
                        self.log_and_update(f"  Error during product image download for one image: {str(e)}")
            else:
                self.log_and_update(f"  No product images found for {product['product_id']} with the current selector.")

            # 2. Process 商品図 (Product Diagram)
            if product.get('diagram_link') or product.get('diagram_href'):
                try:
                    self.log_and_update(f"  Diagram (商品図): Attempting to download for {product['product_id']}...")
                    if self.handle_diagram_download(driver, product, diagram_dir):
                        downloaded_something = True
                        self.log_and_update("  Diagram download process completed successfully.")
                    else:
                        self.log_and_update("  Diagram download process failed.")
                except Exception as e:
                    self.log_and_update(f"  Error downloading diagram: {str(e)}")
            else:
                self.log_and_update(f"  No 商品図 link found for {product['product_id']}.")

            # 2b. Process 分解図 (Exploded Diagram) - only a.btn.md-pdfBtn
            if product.get('bunkaizu_link') or product.get('bunkaizu_href'):
                try:
                    self.log_and_update(f"  分解図: Attempting to download for {product['product_id']}...")
                    if self.handle_bunkaizu_download(driver, product, diagram_dir):
                        downloaded_something = True
                        self.log_and_update("  分解図 download completed successfully.")
                    else:
                        self.log_and_update("  分解図 download did not find eligible PDF.")
                except Exception as e:
                    self.log_and_update(f"  Error downloading 分解図: {str(e)}")
            
            # 3. Process 仕様一覧 (Specifications)
            if product.get('specs_link') or product.get('specs_href'):
                try:
                    self.log_and_update(f"  Specifications (仕様一覧): Attempting to process for {product['product_id']}...")
                    specs_data = self.extract_specifications_data(driver, product.get('specs_link'), product.get('specs_href'), product['product_id'])
                    if specs_data:
                        # Generate template HTML with the extracted specifications data
                        template_html = self.generate_template_html(
                            specs_data, 
                            product['product_id'], 
                            product.get('product_name', ''), 
                            self.extract_manufacturer_from_product_id(product['product_id']),
                            self.extract_series_from_product_name(product.get('product_name', ''))
                        )
                        if template_html:
                            specs_file = os.path.join(product_dir, f"{product['product_id']}_template.html")
                            with open(specs_file, 'w', encoding='utf-8') as f:
                                f.write(template_html)
                            self.log_and_update(f"  Template HTML saved: {specs_file}")
                            downloaded_something = True
                        else:
                            self.log_and_update("  Template HTML generation failed.")
                    else:
                        self.log_and_update("  Specifications data extraction failed.")
                except Exception as e:
                    self.log_and_update(f"  Error processing specifications: {str(e)}")
            else:
                self.log_and_update(f"  No 仕様一覧 link found for {product['product_id']}.")
            
            # Ensure we return to the original window (search results page)
            try:
                if driver.current_window_handle != original_window:
                    self.log_and_update("  Returning to original window after processing.")
                    driver.switch_to.window(original_window)
                else:
                    self.log_and_update("  Already on the original window.")
            except Exception as e:
                self.log_and_update(f"  Error returning to original window: {str(e)}")
                # If original window is closed, try to switch to any available window
                try:
                    available_windows = driver.window_handles
                    if available_windows:
                        self.log_and_update("  Original window closed, switching to first available window.")
                        driver.switch_to.window(available_windows[0])
                except Exception as e:
                    self.log_and_update(f"  Could not switch to any available window: {str(e)}")
            
            return downloaded_something
                
        except Exception as e:
            self.log_and_update(f"  Error processing product: {str(e)}")
            # Try to return to original window even if there's an error
            try:
                if driver.current_window_handle != original_window:
                    driver.switch_to.window(original_window)
            except:
                pass
            return False

    def handle_diagram_download(self, driver, product, diagram_dir):
        """Refactored logic to handle clicking and downloading a diagram."""
        downloaded = False
        link_element = product.get('diagram_link')
        href = product.get('diagram_href')
        if not href and link_element:
            href = link_element.get_attribute('href')
        
        if href:
            self.log_and_update(f"  Link href: {href}")

        # First, try direct download if the href is a PDF link
        if href and href.lower().endswith('.pdf'):
            self.log_and_update("  Direct PDF link found, attempting direct download.")
            if self.download_file(href, diagram_dir):
                return True

        # If it's not a direct link or direct download fails, try clicking
        if link_element:
            try:
                self.log_and_update("  Attempting to click the diagram link.")
                driver.execute_script("arguments[0].scrollIntoView(true);", link_element)
                time.sleep(1)
                
                current_window = driver.current_window_handle
                existing_handles = set(driver.window_handles)
                link_element.click()
                time.sleep(3) # Wait for action to complete

                # Check if a new tab was opened
                new_handles = set(driver.window_handles) - existing_handles
                if new_handles:
                    new_window = list(new_handles)[0]
                    driver.switch_to.window(new_window)
                    self.log_and_update("  New tab detected for diagram. Switched to it.")
                    if self.download_from_current_page(driver, diagram_dir, pdf_only=True, single_file=True):
                        downloaded = True
                    self.log_and_update("  Closing new tab and switching back to original.")
                    driver.close()
                    driver.switch_to.window(current_window)
                else:
                    self.log_and_update("  No new tab opened, checking current page for diagram.")
                    if self.download_from_current_page(driver, diagram_dir, pdf_only=True, single_file=True):
                        downloaded = True
            except Exception as e:
                self.log_and_update(f"  Clicking diagram link failed: {e}")
                # Try to return to original window if there's an error
                try:
                    if driver.current_window_handle != current_window:
                        driver.switch_to.window(current_window)
                except:
                    pass
        
        return downloaded

    def handle_bunkaizu_download(self, driver, product, diagram_dir):
        """Open 分解図 page and download only the a.btn.md-pdfBtn PDF."""
        link_element = product.get('bunkaizu_link')
        href = product.get('bunkaizu_href')
        if not href and link_element:
            try:
                href = link_element.get_attribute('href')
            except Exception:
                href = None

        if not (href or link_element):
            self.log_and_update("  分解図: No link to follow.")
            return False

        original_window = driver.current_window_handle
        try:
            # Prefer clicking if element is present
            if link_element:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", link_element)
                    time.sleep(0.5)
                    existing_handles = set(driver.window_handles)
                    link_element.click()
                    time.sleep(2)
                    new_handles = list(set(driver.window_handles) - existing_handles)
                    if new_handles:
                        driver.switch_to.window(new_handles[0])
                        self.log_and_update("  分解図 page opened in new tab.")
                    else:
                        self.log_and_update("  分解図 opened in same tab.")
                except Exception as e:
                    self.log_and_update(f"  分解図 click failed, trying direct get: {str(e)}")
                    if href:
                        driver.get(href)
                        time.sleep(2)
            else:
                driver.get(href)
                time.sleep(2)

            # Wait for md-pdfBtn presence
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn.md-pdfBtn"))
                )
            except Exception:
                self.log_and_update("  分解図: No a.btn.md-pdfBtn found.")
                return False

            pdf_links = driver.find_elements(By.CSS_SELECTOR, "a.btn.md-pdfBtn")
            self.log_and_update(f"  分解図: Found {len(pdf_links)} md-pdfBtn links.")
            downloaded_any = False
            for i, a in enumerate(pdf_links):
                try:
                    href = a.get_attribute('href')
                    if not href:
                        continue
                    self.log_and_update(f"  分解図: Downloading PDF {i+1}: {href}")
                    if self.download_file(href, diagram_dir):
                        downloaded_any = True
                except Exception as e:
                    self.log_and_update(f"  分解図: Failed to download one PDF: {str(e)}")
                    continue

            return downloaded_any
        finally:
            try:
                if driver.current_window_handle != original_window and original_window in driver.window_handles:
                    driver.close()
                    driver.switch_to.window(original_window)
            except Exception:
                try:
                    if original_window in driver.window_handles:
                        driver.switch_to.window(original_window)
                except Exception:
                    pass

    def download_from_current_page(self, driver, diagram_dir, pdf_only=False, single_file=False):
        """Download diagrams from the current page."""
        try:
            self.log_and_update(f"  Analyzing current page for downloads...")
            current_url = driver.current_url
            time.sleep(2)

            # Method 1: If the current URL is a direct link to a file
            file_extensions = ['.pdf'] if pdf_only else ['.pdf', '.jpg', '.jpeg', '.png', '.gif']
            if any(ext in current_url.lower() for ext in file_extensions):
                self.log_and_update("  Current URL is a direct file link. Attempting download with Selenium...")
                filename = self.download_file_with_selenium(driver, diagram_dir)
                if filename:
                    self.log_and_update(f"  Successfully downloaded current page: {filename}")
                    return True

            # Method 2: Look for download links on the current page
            links_to_download = []
            all_links = driver.find_elements(By.TAG_NAME, "a")
            for link in all_links:
                href = link.get_attribute('href')
                if href and any(href.lower().endswith(ext) for ext in file_extensions):
                    links_to_download.append(href)

            self.log_and_update(f"  Found {len(links_to_download)} potential file links on this page.")

            if not links_to_download:
                self.log_and_update("  No direct links found on the page.")

            for i, link_url in enumerate(links_to_download):
                self.log_and_update(f"  Attempting download from link {i+1}: {link_url}")
                if self.download_file(link_url, diagram_dir):
                    if single_file:
                        return True
            
            return False
            
        except Exception as e:
            self.log_and_update(f"  Error downloading from current page: {str(e)}")
            return False

    def download_file_with_selenium(self, driver, directory):
        """Download file using Selenium, deriving the filename from the URL."""
        try:
            current_url = driver.current_url
            self.log_and_update(f"    Downloading file from current URL: {current_url}")
            
            # Get filename from URL
            parsed_url = urlparse(current_url)
            filename = os.path.basename(parsed_url.path)
            
            # If filename is empty or invalid, create one
            if not filename or '.' not in filename:
                self.log_and_update("    Filename from URL is invalid, generating new one.")
                if '.pdf' in current_url.lower():
                    ext = '.pdf'
                elif any(img_ext in current_url.lower() for img_ext in ['.jpg', '.jpeg']):
                    ext = 'jpg'
                elif '.png' in current_url.lower():
                    ext = '.png'
                elif '.gif' in current_url.lower():
                    ext = '.gif'
                else:
                    ext = '.tmp'
                filename = f"download_{int(time.time())}{ext}"
            
            filename = "".join(c for c in filename if c.isalnum() or c in "._-")
            filepath = os.path.join(directory, filename)
            
            if os.path.exists(filepath):
                self.log_and_update("    File already exists, renaming to avoid overwrite.")
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{int(time.time())}{ext}"
                filepath = os.path.join(directory, filename)

            js_code = """
            const callback = arguments[arguments.length - 1];
            const url = arguments[0];
            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok: ' + response.statusText);
                    }
                    return response.arrayBuffer();
                })
                .then(buffer => callback(Array.from(new Uint8Array(buffer))))
                .catch(error => callback({error: error.message}));
            """
            
            driver.set_script_timeout(30)
            result = driver.execute_async_script(js_code, current_url)
            
            if isinstance(result, dict) and 'error' in result:
                self.log_and_update(f"    Selenium download via JS failed: {result['error']}")
                return None

            file_content = bytes(result)
            with open(filepath, 'wb') as f:
                f.write(file_content)
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                self.log_and_update(f"    Successfully downloaded via Selenium: {filename} ({os.path.getsize(filepath)} bytes)")
                return filename
            else:
                self.log_and_update(f"    Selenium download failed - file is empty or missing")
                if os.path.exists(filepath): os.remove(filepath)
                return None
                
        except Exception as e:
            self.log_and_update(f"    Error in Selenium download: {str(e)}")
            return None

    def extract_specifications_data(self, driver, specs_link, specs_href, product_id):
        """Extract specifications table data and return as structured data"""
        self.log_and_update("  Starting specifications data extraction process.")
        original_window = driver.current_window_handle
        try:
            # Click the specifications link
            try:
                if specs_link is not None:
                    self.log_and_update("    Clicking on specs link element.")
                    driver.execute_script("arguments[0].scrollIntoView(true);", specs_link)
                    time.sleep(1)
                    specs_link.click()
                    time.sleep(3)
                elif specs_href:
                    self.log_and_update(f"    Navigating to specs URL: {specs_href}")
                    driver.get(specs_href)
                    time.sleep(3)
                else:
                    self.log_and_update("    No specifications link or URL available. Skipping.")
                    return None
            except Exception as e:
                self.log_and_update(f"    Error clicking specs link: {str(e)}")
                return None
            
            # Check if a new window/tab opened
            if len(driver.window_handles) > 1:
                new_window = [h for h in driver.window_handles if h != original_window][0]
                driver.switch_to.window(new_window)
                self.log_and_update("    Switched to new window for specifications.")
            
            time.sleep(2)
            
            specs_table = None
            table_selectors = ["[class*='spec'] table", "[class*='table']", "table"]
            
            for selector in table_selectors:
                try:
                    self.log_and_update(f"    Attempting to find table with selector: {selector}")
                    tables = driver.find_elements(By.CSS_SELECTOR, selector)
                    if not tables:
                        self.log_and_update(f"    No tables found with selector: {selector}")
                        continue
                    
                    for table in tables:
                        if any(k in table.text for k in ['基本情報', '仕様', '質量', '発売時期']):
                            specs_table = table
                            self.log_and_update(f"    Found specifications table with keyword match.")
                            break
                    if specs_table:
                        break
                except Exception as e:
                    self.log_and_update(f"    Error finding table with selector {selector}: {str(e)}")
            
            if not specs_table:
                self.log_and_update(f"    No specifications table found on the page.")
                if len(driver.window_handles) > 1 and driver.current_window_handle != original_window:
                    self.log_and_update("    Closing new window and returning to original.")
                    driver.close()
                    driver.switch_to.window(original_window)
                return None
            
            table_data = self.extract_table_data(specs_table)
            self.log_and_update(f"    Extracted {len(table_data)} rows of table data.")
            
            if len(driver.window_handles) > 1 and driver.current_window_handle != original_window:
                self.log_and_update("    Closing new window and returning to original.")
                driver.close()
                driver.switch_to.window(original_window)
            
            return table_data
            
        except Exception as e:
            self.log_and_update(f"    Error extracting specifications data: {str(e)}")
            try:
                if len(driver.window_handles) > 1 and driver.current_window_handle != original_window:
                    self.log_and_update("    Error occurred, but attempting to close new window and return to original.")
                    driver.close()
                    driver.switch_to.window(original_window)
            except:
                pass
            return None

    def extract_manufacturer_from_product_id(self, product_id):
        """Extract manufacturer name from product ID"""
        try:
            if product_id.startswith('TCF') or product_id.startswith('TCA'):
                return "TOTO（トートー）"
            elif product_id.startswith('LIXIL') or product_id.startswith('INAX'):
                return "LIXIL（リクシル）"
            elif product_id.startswith('TOTO'):
                return "TOTO（トートー）"
            else:
                return "Unknown Manufacturer"
        except Exception:
            return "Unknown Manufacturer"

    def extract_series_from_product_name(self, product_name):
        """Extract series information from product name"""
        try:
            if not product_name:
                return "Unknown Series"
            
            # Look for common series patterns
            if "アプリコット" in product_name:
                return "アプリコットシリーズ"
            elif "ネオレスト" in product_name:
                return "ネオレストシリーズ"
            elif "サティス" in product_name:
                return "サティスシリーズ"
            elif "パブリック" in product_name:
                return "パブリック向ウォシュレット"
            else:
                return "Unknown Series"
        except Exception:
            return "Unknown Series"

    def extract_table_data(self, table_element):
        """Extract table data exactly as it appears row by row, column by column"""
        self.log_and_update("      Extracting table data row by row...")
        table_data = []
        try:
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            
            for i, row in enumerate(rows):
                try:
                    # Get all th and td elements in this row
                    all_cells = row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")
                    
                    if not all_cells:
                        continue
                    
                    # Extract text from each cell
                    row_data = []
                    for cell in all_cells:
                        cell_text = cell.text.strip()
                        rowspan = cell.get_attribute("rowspan")
                        colspan = cell.get_attribute("colspan")
                        cell_type = cell.tag_name
                        
                        row_data.append({
                            'text': cell_text,
                            'rowspan': int(rowspan) if rowspan else 1,
                            'colspan': int(colspan) if colspan else 1,
                            'type': cell_type
                        })
                    
                    # Store the complete row data
                    table_data.append({
                        'row_index': i,
                        'cells': row_data
                    })
                    
                    self.log_and_update(f"      - Row {i}: {len(row_data)} cells")
                    for j, cell in enumerate(row_data):
                        self.log_and_update(f"        Cell {j}: '{cell['text']}' ({cell['type']}, rowspan={cell['rowspan']}, colspan={cell['colspan']})")
                
                except Exception as e:
                    self.log_and_update(f"      - Error processing table row {i}: {str(e)}")
                    continue
        except Exception as e:
            self.log_and_update(f"      - Error extracting table data: {str(e)}")
        return table_data

    def generate_rakuten_html(self, table_data, product_id):
        """Generate HTML for Rakuten EC site based on specifications data with 3-column structure"""
        self.log_and_update("      Generating Rakuten HTML...")
        try:
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{product_id} - 商品仕様</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        .section-title {{ background-color: #333; color: white; padding: 10px; font-weight: bold; border-radius: 4px; margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f8f9fa; font-weight: bold; width: 25%; }}
        td.primary {{ background-color: #f8f9fa; width: 35%; }}
        td.secondary {{ background-color: #f8f9fa; width: 40%; }}
        .product-info {{ background-color: #e9ecef; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
        .product-id {{ font-size: 18px; font-weight: bold; color: #007bff; }}
        .table-header {{ background-color: #333; color: white; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>商品仕様書</h1>
        <div class="product-info">
            <div class="product-id">品番: {product_id}</div>
        </div>
"""
            
            last_section = None
            for item in table_data:
                section = item['section']
                if section != last_section:
                    if last_section is not None:
                        html_content += "        </table>\n"
                    html_content += f"        <div class=\"section-title\">{section}</div>\n"
                    html_content += "        <table>\n"
                    html_content += "            </tr>\n"
                    last_section = section
                
                item_name = item['item'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                primary_value = item['primary_value'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                secondary_value = item['secondary_value'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                # Use dash for empty secondary values
                if not secondary_value or secondary_value == "":
                    secondary_value = "-"
                
                html_content += f"            <tr>\n"
                html_content += f"                <th>{item_name}</th>\n"
                html_content += f"                <td class=\"primary\">{primary_value}</td>\n"
                html_content += f"                <td class=\"secondary\">{secondary_value}</td>\n"
                html_content += f"            </tr>\n"

            if last_section is not None:
                html_content += "        </table>\n"
            
            html_content += """
    </div>
</body>
</html>"""
            self.log_and_update("      Rakuten HTML generated successfully.")
            return html_content
        except Exception as e:
            self.log_and_update(f"      Error generating Rakuten HTML: {str(e)}")
            return None

    def generate_template_html(self, table_data, product_id, product_name="", manufacturer="", series=""):
        """Generate HTML following the template structure with product-specific information"""
        self.log_and_update("      Generating template HTML...")
        try:
            # Extract manufacturer from product_id if not provided
            if not manufacturer:
                if product_id.startswith('TCF') or product_id.startswith('TCA'):
                    manufacturer = "TOTO（トートー）"
                else:
                    manufacturer = "Unknown Manufacturer"
            
            # Format product ID with color name if available
            formatted_product_id = self.format_product_id_with_color(product_id)
            
            # Generate specifications table HTML
            specs_table_html = self.generate_specs_table_html(table_data)
            
            # Generate features HTML
            features_html = self.generate_features_html(table_data)
            
            html_content = f"""<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Document</title>
</head>

<body>

  <!--  
コメット　
商品番号　{product_id}
https://www.com-et.com/jp/item_color_search/searchStr={product_id.replace('#', '%23')}/isHaiban=1/kensaku_info=2/hinban={product_id.split('#')[0]}/renban=1/isFromScale=0/isNC=1/datatype=1/
-->


  <!-- ●●●●● コメットから情報取得 -->
  <br>
  <br>
  <font size="+1">
    <b>
      メーカー：{manufacturer}
      <br>
      品&nbsp;&nbsp;番&nbsp;&nbsp;&nbsp;：◆{formatted_product_id}
      <br>
      商&nbsp;品&nbsp;名&nbsp;：{product_name if product_name else 'Unknown Product'}
      <br>
      シリーズ：{series if series else 'Unknown Series'}
      <br>
    </b>
  </font>
  <br>
  <br>
  <!-- /// ●●●●● コメットから情報取得 -->


  <!-- ◆◆◆　定型文 -->
  ※商品画像・カラーは、イメージです。
  <br>
  ※詳しい施工方法や商品詳細については、カタログやメーカー様にてご確認ください。
  <br>
  <!-- ◆◆◆　ここに納期等入れる -->
  <br>
  <!-- /// ◆◆◆　定型文 -->


  <!-- ●●●●● コメットから情報取得 ●●●●● 構成品 -->
  【 セット品番 ：{formatted_product_id} 】
  <br>
  <br>{formatted_product_id}
  <br>
  -------------------------------------------------------
  <br>
  構成品番 ： ◆{formatted_product_id}
  <br>
  商品名 ： {product_name if product_name else 'Unknown Product'}
  <br>
  -------------------------------------------------------
  <br>
  <br>
  <!-- /// コメットから情報取得 ●●●●● 構成品 -->


  <!-- ●●●●● コメットから情報取得 ●●●●● 仕様一覧 -->
  【 仕様 】
  <br>
{specs_table_html}
  <br><br>
  【 仕様 】
{features_html}
  <!-- /// コメットから情報取得 ●●●●● 仕様一覧 -->




</html>"""
            
            self.log_and_update("      Template HTML generated successfully.")
            return html_content
        except Exception as e:
            self.log_and_update(f"      Error generating template HTML: {str(e)}")
            return None

    def generate_specs_table_html(self, table_data):
        """Generate the specifications table HTML exactly as the original table structure"""
        try:
            html = """  <table bgcolor="#000000" cellspacing="1" cellpadding="3">

"""
            
            # Process each row exactly as it appears in the original table
            for row_data in table_data:
                cells = row_data['cells']
                
                if not cells:
                    continue
                
                # Start the table row
                html += "    <tr>\n"
                
                # Process each cell in the row
                for cell in cells:
                    cell_text = cell['text'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    rowspan = cell['rowspan']
                    colspan = cell['colspan']
                    cell_type = cell['type']
                    
                    # Determine alignment and background color based on cell type
                    if cell_type == 'th':
                        bgcolor = "#F5F5F5"
                        align = "left"
                    else:
                        bgcolor = "#FFFFFF"
                        align = "left"
                    
                    # Build the cell attributes
                    attributes = f'align="{align}" bgcolor="{bgcolor}"'
                    if rowspan > 1:
                        attributes += f' rowspan="{rowspan}"'
                    if colspan > 1:
                        attributes += f' colspan="{colspan}"'
                    
                    # Add the cell
                    html += f"      <{cell_type} {attributes}>{cell_text}</{cell_type}>\n"
                
                # Close the table row
                html += "    </tr>\n\n"
            
            html += "  </table>"
            return html
        except Exception as e:
            self.log_and_update(f"      Error generating specs table HTML: {str(e)}")
            return "  <table bgcolor=\"#000000\" cellspacing=\"1\" cellpadding=\"3\">\n  </table>"

    def generate_features_html(self, table_data):
        """Generate the features section HTML following the template format"""
        try:
            # Extract features from the table data
            cleaning_features = []
            comfort_features = []
            eco_features = []
            hygiene_features = []
            
            # Process each row to extract features
            for row_data in table_data:
                cells = row_data['cells']
                
                # Look for feature-related items in the table
                for i, cell in enumerate(cells):
                    if cell['type'] == 'th' and cell['text']:
                        item_name = cell['text']
                        
                        # Get the corresponding value from the next cell
                        value = ""
                        if i + 1 < len(cells) and cells[i + 1]['type'] == 'td':
                            value = cells[i + 1]['text']
                        
                        # Categorize based on item names
                        if any(keyword in item_name for keyword in ['洗浄', '水勢', 'ビデ', 'おしり']):
                            if value and value != "-":
                                cleaning_features.append(f"・{value}")
                        elif any(keyword in item_name for keyword in ['暖房', '脱臭', 'リモコン', 'センサ', '音姫', '電子音']):
                            if value and value != "-":
                                comfort_features.append(f"・{value}")
                        elif any(keyword in item_name for keyword in ['節電', 'オフ', 'エコ']):
                            if value and value != "-":
                                eco_features.append(f"・{value}")
                        elif any(keyword in item_name for keyword in ['ノズル', '抗菌', 'クリーニング', 'クリーン', '便器', '便座']):
                            if value and value != "-":
                                hygiene_features.append(f"・{value}")
            
            html = ""
            
            if cleaning_features:
                html += "  <br><b>洗浄機能</b><br>" + "<br>".join(cleaning_features[:5])  # Limit to 5 features
            if comfort_features:
                html += "<br><b>快適機能</b><br>" + "<br>".join(comfort_features[:10])  # Limit to 10 features
            if eco_features:
                html += "<br><b>エコ機能</b><br>" + "<br>".join(eco_features[:5])  # Limit to 5 features
            if hygiene_features:
                html += "<br><b>清潔機能</b><br>" + "<br>".join(hygiene_features[:10])  # Limit to 10 features
            
            return html
        except Exception as e:
            self.log_and_update(f"      Error generating features HTML: {str(e)}")
            return ""

    def download_direct_link(self, diagram, product_id):
        """Download a diagram from a direct link"""
        try:
            self.log_and_update(f"  Downloading direct link: {diagram['text']}")
            
            # Create directory structure
            product_dir = os.path.join(self.output_dir, product_id)
            diagram_dir = os.path.join(product_dir, config.DIAGRAM_FOLDER_NAME)
            
            os.makedirs(diagram_dir, exist_ok=True)
            self.log_and_update(f"  Ensured diagram directory exists: {diagram_dir}")
            
            # Download the file
            filename = self.download_file(diagram['url'], diagram_dir)
            if filename:
                self.log_and_update(f"  Downloaded: {filename}")
                return True
            else:
                self.log_and_update(f"  Failed to download: {diagram['url']}")
                return False
                
        except Exception as e:
            self.log_and_update(f"  Error downloading direct link: {str(e)}")
            return False

    def process_product_page(self, driver, product, product_id):
        try:
            self.log_and_update(f"Processing product page: {product['text']}")
            
            # Navigate to product page
            driver.get(product['url'])
            time.sleep(config.PAGE_LOAD_TIMEOUT)
            self.log_and_update("  Navigated to product page and waited for load.")
            
            # Get page source
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look for 商品図 (product diagram) section
            diagram_links = []
            
            # Search for text containing 商品図
            diagram_sections = soup.find_all(text=re.compile(r'商品図'))
            
            for section in diagram_sections:
                parent = section.parent
                # Look for links in the same section
                links = parent.find_all('a', href=True)
                for link in links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(driver.current_url, href)
                        diagram_links.append({
                            'url': full_url,
                            'text': link.get_text(strip=True)
                        })
            
            # Also search for common file extensions
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href')
                if href:
                    # Check if it's a downloadable file
                    if any(href.lower().endswith(ext) for ext in config.SUPPORTED_EXTENSIONS):
                        full_url = urljoin(driver.current_url, href)
                        diagram_links.append({
                            'url': full_url,
                            'text': link.get_text(strip=True) or os.path.basename(href)
                        })
            
            if not diagram_links:
                self.log_and_update(f"  No diagrams found for {product['text']}")
                return False
            
            # Create directory structure
            product_dir = os.path.join(self.output_dir, product_id)
            diagram_dir = os.path.join(product_dir, config.DIAGRAM_FOLDER_NAME)
            
            os.makedirs(diagram_dir, exist_ok=True)
            
            # Download diagrams
            downloaded = False
            for diagram in diagram_links:
                try:
                    self.log_and_update(f"  Attempting to download diagram from product page: {diagram['url']}")
                    filename = self.download_file(diagram['url'], diagram_dir)
                    if filename:
                        self.log_and_update(f"  Downloaded: {filename}")
                        downloaded = True
                except Exception as e:
                    self.log_and_update(f"  Failed to download {diagram['url']}: {str(e)}")
            
            return downloaded
            
        except Exception as e:
            self.log_and_update(f"  Error processing page: {str(e)}")
            return False
    
    def download_file(self, url, directory):
        try:
            self.log_and_update(f"    Starting file download for URL: {url}")
            
            # Get filename from URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # Clean up filename
            if filename:
                filename = filename.split('?')[0]
                filename = "".join(c for c in filename if c.isalnum() or c in "._-")
            
            if not filename or '.' not in filename:
                self.log_and_update("    Filename from URL is invalid, generating one based on content type.")
                try:
                    headers = self.get_browser_headers()
                    response = requests.head(url, headers=headers, timeout=config.DOWNLOAD_TIMEOUT)
                    response.raise_for_status()
                    content_type = response.headers.get('content-type', '')
                    
                    if 'pdf' in content_type:
                        filename = f"diagram_{int(time.time())}.pdf"
                    elif 'image' in content_type:
                        ext = content_type.split('/')[-1]
                        if ext in ['jpeg', 'jpg']:
                            ext = 'jpg'
                        elif ext in ['png', 'gif', 'bmp', 'tiff']:
                            ext = ext
                        else:
                            ext = 'jpg'
                        filename = f"image_{int(time.time())}.{ext}"
                    else:
                        filename = f"file_{int(time.time())}.dat"
                except Exception as e:
                    self.log_and_update(f"    Failed to get content type for filename generation: {str(e)}")
                    filename = f"file_{int(time.time())}.dat"
            
            filepath = os.path.join(directory, filename)
            
            if os.path.exists(filepath):
                self.log_and_update("    File already exists, appending timestamp to filename.")
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{int(time.time())}{ext}"
                filepath = os.path.join(directory, filename)
            
            headers = self.get_browser_headers()
            response = requests.get(url, headers=headers, timeout=config.DOWNLOAD_TIMEOUT, stream=True)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if 'text/html' in content_type:
                self.log_and_update("    Warning: Link leads to an HTML page, not a direct file. Skipping direct download.")
                return None
                
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=config.CHUNK_SIZE):
                    f.write(chunk)
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                self.log_and_update(f"    Successfully downloaded: {filename} ({os.path.getsize(filepath)} bytes)")
                return filename
            else:
                self.log_and_update(f"    File download failed - file is empty or missing")
                return None
            
        except Exception as e:
            self.log_and_update(f"    Download failed: {str(e)}")
            return None

    def get_browser_headers(self):
        """Get realistic browser headers to avoid 403 errors"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.com-et.com/jp/'
        }

    def download_product_image(self, driver, image_info, diagram_dir):
        """Download a product image from the href link."""
        try:
            href = image_info['href']
            alt_text = image_info['alt']
            
            self.log_and_update(f"    Downloading image for {alt_text}: {href}")
            
            # Direct download from the href link
            if self.download_file(href, diagram_dir):
                self.log_and_update(f"    Successfully downloaded image for {alt_text}")
                return True
            else:
                self.log_and_update(f"    Failed to download image for {alt_text}")
                return False
                
        except Exception as e:
            self.log_and_update(f"    Error downloading image: {str(e)}")
            return False
    
    def update_status(self, message):
        self.status_text.set(message)
        self.root.update_idletasks()
    
    def update_results(self, message):
        self.results_text.insert(tk.END, message)
        self.results_text.see(tk.END)
        self.root.update_idletasks()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ComEtCrawler()
    app.run()