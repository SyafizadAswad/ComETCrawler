import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import time
import requests
from urllib.parse import urljoin, urlparse
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
import config

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
        
        # Output directory
        self.output_dir = config.OUTPUT_DIR
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.setup_gui()
        
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
        
        # Start search in separate thread
        thread = threading.Thread(target=self.perform_search, args=(product_id,))
        thread.daemon = True
        thread.start()
        
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
                self.update_status("Initializing Chrome driver (method 1)...")
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                self.update_status("Chrome driver initialized successfully!")
            except Exception as e1:
                error_messages.append(f"Method 1 failed: {str(e1)}")
                
                # Method 2: Try with ChromeService
                try:
                    self.update_status("Trying alternative Chrome driver initialization...")
                    from selenium.webdriver.chrome.service import Service as ChromeService
                    from webdriver_manager.chrome import ChromeDriverManager
                    
                    service = ChromeService(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    self.update_status("Chrome driver initialized successfully!")
                except Exception as e2:
                    error_messages.append(f"Method 2 failed: {str(e2)}")
                    
                    # Method 3: Try with minimal options
                    try:
                        self.update_status("Trying with minimal Chrome options...")
                        minimal_options = Options()
                        minimal_options.add_argument("--headless")
                        minimal_options.add_argument("--no-sandbox")
                        minimal_options.add_argument("--disable-dev-shm_usage")
                        minimal_options.add_argument("--disable-gpu")
                        minimal_options.add_argument("--disable-extensions")
                        minimal_options.add_argument("--disable-plugins")
                        
                        service = Service(ChromeDriverManager().install())
                        driver = webdriver.Chrome(service=service, options=minimal_options)
                        self.update_status("Chrome driver initialized with minimal options!")
                    except Exception as e3:
                        error_messages.append(f"Method 3 failed: {str(e3)}")
                        
                        # Method 4: Try without headless mode
                        try:
                            self.update_status("Trying without headless mode...")
                            visible_options = Options()
                            visible_options.add_argument("--no-sandbox")
                            visible_options.add_argument("--disable-dev-shm_usage")
                            visible_options.add_argument("--disable-gpu")
                            visible_options.add_argument("--disable-extensions")
                            visible_options.add_argument("--disable-plugins")
                            # Remove headless mode for debugging
                            
                            service = Service(ChromeDriverManager().install())
                            driver = webdriver.Chrome(service=service, options=visible_options)
                            self.update_status("Chrome driver initialized in visible mode!")
                        except Exception as e4:
                            error_messages.append(f"Method 4 failed: {str(e4)}")
                            
                            # Final attempt: Try with system PATH
                            try:
                                self.update_status("Trying with system ChromeDriver...")
                                driver = webdriver.Chrome(options=chrome_options)
                                self.update_status("Chrome driver initialized from system PATH!")
                            except Exception as e5:
                                error_messages.append(f"Method 5 failed: {str(e5)}")
                                raise Exception(f"All Chrome driver initialization methods failed. Errors: {'; '.join(error_messages)}. Please run 'python troubleshoot_chrome.py' for detailed diagnostics.")
            
            if driver is None:
                raise Exception("Failed to initialize Chrome driver after all attempts.")
            
            try:
                self.update_status("Navigating to COM-ET website...")
                driver.get(config.WEBSITE_URL)
                
                # Wait for page to load
                WebDriverWait(driver, config.SEARCH_TIMEOUT).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                self.update_status("Looking for search bar...")
                
                # Try to find search input field with better detection
                search_input = None
                search_selectors = config.SEARCH_INPUT_PATTERNS
                
                # First try the configured selectors
                for selector in search_selectors:
                    try:
                        search_input = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if search_input and search_input.is_displayed() and search_input.is_enabled():
                            break
                    except:
                        continue
                
                # If no search input found, try to find any visible input field
                if not search_input:
                    try:
                        inputs = driver.find_elements(By.TAG_NAME, "input")
                        for inp in inputs:
                            if (inp.get_attribute("type") in ["text", "search"] and 
                                inp.is_displayed() and inp.is_enabled()):
                                search_input = inp
                                break
                    except:
                        pass
                
                # If still no search input, try to find by placeholder or name
                if not search_input:
                    try:
                        search_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='検索'], input[name*='search'], input[id*='search']")
                    except:
                        pass
                
                if not search_input:
                    # Last resort: try to find any input that might be a search box
                    try:
                        all_inputs = driver.find_elements(By.TAG_NAME, "input")
                        for inp in all_inputs:
                            if inp.is_displayed() and inp.is_enabled():
                                placeholder = inp.get_attribute("placeholder") or ""
                                name = inp.get_attribute("name") or ""
                                id_attr = inp.get_attribute("id") or ""
                                
                                if any(keyword in (placeholder + name + id_attr).lower() for keyword in ['search', '検索', 'q', 'query']):
                                    search_input = inp
                                    break
                    except:
                        pass
                
                if not search_input:
                    # Try one more approach: look for any form with a text input
                    try:
                        forms = driver.find_elements(By.TAG_NAME, "form")
                        for form in forms:
                            inputs = form.find_elements(By.TAG_NAME, "input")
                            for inp in inputs:
                                if inp.get_attribute("type") in ["text", "search"] and inp.is_displayed():
                                    search_input = inp
                                    break
                            if search_input:
                                break
                    except:
                        pass
                
                if not search_input:
                    raise Exception("Could not find search input field. Please check if the website structure has changed.")
                
                # Additional verification that the element is ready
                try:
                    # Wait for element to be present and visible
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of(search_input)
                    )
                except:
                    self.update_status("Warning: Search input may not be fully ready")
                
                self.update_status(f"Entering product ID: {product_id}")
                
                # Wait for element to be interactable
                try:
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, search_input.tag_name + "[value='" + search_input.get_attribute("value") + "']"))
                    )
                except:
                    # If that fails, try a simpler approach
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.TAG_NAME, "input"))
                        )
                    except:
                        pass
                
                # Clear and enter product ID with better interaction
                try:
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
                except Exception as e:
                    # Fallback: try JavaScript interaction
                    self.update_status("Trying JavaScript interaction...")
                    try:
                        driver.execute_script(f"arguments[0].value = '{product_id}';", search_input)
                        driver.execute_script("arguments[0].form.submit();", search_input)
                    except:
                        # Last resort: try to find and click a search button
                        try:
                            search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .search-button, .btn-button")
                            search_button.click()
                        except:
                            raise Exception(f"Could not interact with search field: {str(e)}")
                
                # Wait for search results to load
                self.update_status("Waiting for search results to load...")
                time.sleep(5)  # Give more time for dynamic content
                
                # Wait for search results to be visible
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except:
                    pass
                
                # Check if we're still on the search page (search might have failed)
                current_url = driver.current_url
                if "search" not in current_url.lower() and "result" not in current_url.lower():
                    # Try alternative search method using JavaScript
                    self.update_status("Search may have failed, trying alternative method...")
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
                    except:
                        pass
                
                # Get current page source
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Look for product containers on search results page
                self.update_status("Analyzing search results page for product containers...")
                
                # Find product containers using Selenium for better interaction
                product_containers = []
                
                # Wait for search results to be visible
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                    )
                except:
                    pass
                
                # Look for product containers with various selectors
                container_selectors = [
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
                            product_containers = containers
                            self.update_status(f"Found {len(containers)} product containers using selector: {selector}")
                            break
                    except:
                        continue
                
                # If no containers found with specific selectors, try to find by content
                if not product_containers:
                    self.update_status("Looking for product containers by content...")
                    try:
                        # Look for elements containing product information
                        all_divs = driver.find_elements(By.TAG_NAME, "div")
                        for div in all_divs:
                            try:
                                div_text = div.text
                                if any(keyword in div_text for keyword in ['品番', '商品名', '商品図', 'Product']):
                                    product_containers.append(div)
                            except:
                                continue
                    except:
                        pass
                
                if not product_containers:
                    self.update_status("No product containers found, trying alternative approach...")
                    # Try to find any elements that might contain products
                    try:
                        all_elements = driver.find_elements(By.CSS_SELECTOR, "div, li, section")
                        for element in all_elements:
                            try:
                                element_text = element.text
                                if '品番' in element_text and '商品図' in element_text:
                                    product_containers.append(element)
                            except:
                                continue
                    except:
                        pass
                
                self.update_status(f"Found {len(product_containers)} potential product containers")
                
                # Process each product container
                products_data = []
                # Use a set to keep track of processed product IDs to avoid duplicates
                seen_product_ids = set() 

                for i, container in enumerate(product_containers):
                    try:
                        self.update_status(f"Extracting info from container {i+1}/{len(product_containers)}")
                        
                        # Extract product information from container
                        product_info = self.extract_product_info(container, driver)
                        
                        if product_info and product_info['product_id'] not in seen_product_ids:
                            products_data.append(product_info)
                            seen_product_ids.add(product_info['product_id'])
                            self.update_results(f"Found product: {product_info['product_id']} - {product_info['product_name']}\n")
                        elif product_info and product_info['product_id'] in seen_product_ids:
                            self.update_results(f"Skipping duplicate product: {product_info['product_id']}\n")
                        
                    except Exception as e:
                        self.update_results(f"Error extracting from container {i+1}: {str(e)}\n")
                
                if not products_data:
                    self.update_results("No products found in containers. Trying fallback method...\n")
                    # Fallback: try to find any 商品図 links on the page
                    fallback_products = self.fallback_product_detection(driver)
                    for product in fallback_products:
                        if product['product_id'] not in seen_product_ids:
                            products_data.append(product)
                            seen_product_ids.add(product['product_id'])

                self.update_status(f"Found {len(products_data)} unique products. Starting downloads...")
                self.update_results(f"Found {len(products_data)} unique products to process.\n\n")
                
                if not products_data:
                    self.update_results("No products found. The search might not have returned any results.\n")
                    return
                
                # Process each product and download diagrams
                downloaded_count = 0
                for i, product in enumerate(products_data):
                    self.update_status(f"Processing product {i+1}/{len(products_data)}: {product['product_id']}")
                    self.progress_var.set((i / len(products_data)) * 100)
                    
                    try:
                        if self.process_product_diagrams(driver, product):
                            downloaded_count += 1
                    except Exception as e:
                        self.update_results(f"Error processing {product['product_id']}: {str(e)}\n")
                
                self.progress_var.set(100)
                self.update_status(f"Search completed. Downloaded items for {downloaded_count} products.")
                self.update_results(f"\nSearch completed. Downloaded items for {downloaded_count} products.\n")
                
            finally:
                driver.quit()
                
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.update_results(f"Error occurred: {str(e)}\n")
        finally:
            self.is_searching = False
            self.search_button.config(state='normal')
    
    def extract_product_info(self, container, driver):
        """
        Extract product information from a container element,
        prioritizing diagram links that precisely match the product_id.
        """
        try:
            # Get container text
            container_text = container.text
            
            # Extract product ID (品番)
            product_id = None
            import re
            product_id_match = re.search(r'◆([A-Z0-9]+)', container_text)
            if product_id_match:
                product_id = product_id_match.group(1)
            
            # Extract product name (商品名)
            product_name = "Unknown Product"
            lines = container_text.split('\n')
            for line in lines:
                if '商品名' in line or 'Product' in line:
                    product_name = line.strip()
                    break
            
            if not product_id:
                return None
            
            diagram_link = None
            specs_link = None
            product_images = [] 
            diagram_href = None
            specs_href = None
            
            all_links_in_container = container.find_elements(By.TAG_NAME, "a")
            
            # --- Diagram Link Selection Logic ---
            # Priority 1: Find a diagram link that explicitly contains the product_id as a distinct part in its href
            found_exact_diagram = False
            for link in all_links_in_container:
                href = link.get_attribute('href')
                link_text = link.text.strip()
                if '商品図' in link_text and href:
                    parsed_path = urlparse(href).path
                    filename = os.path.basename(parsed_path)
                    
                    # Use regex word boundaries to match the exact product_id in the filename/path
                    # This prevents matching "CS902B" within "CS902BVN"
                    if re.search(r'\b' + re.escape(product_id) + r'\b', filename, re.IGNORECASE):
                        diagram_link = link
                        diagram_href = href
                        found_exact_diagram = True
                        break # Found the most relevant one, break early
            
            # Priority 2: If no exact match, fall back to general 商品図 link within the container
            if not found_exact_diagram:
                for link in all_links_in_container:
                    href = link.get_attribute('href')
                    link_text = link.text.strip()
                    if '商品図' in link_text:
                        diagram_link = link
                        diagram_href = href
                        break # Take the first general 商品図 link found
                    elif href and ('diagram' in href.lower() or 'drawing' in href.lower()):
                        if not diagram_link: # Only assign if nothing better found yet
                            diagram_link = link
                            diagram_href = href

            # --- Specifications Link Selection Logic ---
            for link in all_links_in_container:
                href = link.get_attribute('href')
                link_text = link.text.strip()
                if '仕様一覧' in link_text:
                    specs_link = link
                    specs_href = href
                    break # Found the specs link, break

            # --- Product Images Selection Logic ---
            # Find product images with the specific prefix. 
            # If images for other 品番 exist, but have different prefixes, this selector might miss them.
            images = container.find_elements(By.CSS_SELECTOR, "img[src^='https://search.toto.jp/img/']")
            for img in images:
                product_images.append(img)
            
            return {
                'product_id': product_id,
                'product_name': product_name,
                'container': container,
                'diagram_link': diagram_link,
                'diagram_href': diagram_href,
                'specs_link': specs_link,
                'specs_href': specs_href,
                'product_images': product_images, # List of images to download
                'container_text': container_text
            }
            
        except Exception as e:
            self.update_results(f"Error extracting product info: {str(e)}\n")
            return None

    def fallback_product_detection(self, driver):
        """Fallback method to detect products when containers are not found"""
        products_data = []
        try:
            # Look for any 商品図 links on the page
            diagram_links = driver.find_elements(By.XPATH, "//a[contains(text(), '商品図')]")
            
            for i, link in enumerate(diagram_links):
                try:
                    # Try to find product ID in nearby text
                    parent = link.find_element(By.XPATH, "./..")
                    parent_text = parent.text
                    
                    import re
                    product_id_match = re.search(r'◆([A-Z0-9]+)', parent_text)
                    if product_id_match:
                        product_id = product_id_match.group(1)
                    else:
                        product_id = f"Product_{i+1}"
                    
                    products_data.append({
                        'product_id': product_id,
                        'product_name': f"Product {i+1}",
                        'diagram_link': link,
                        'container_text': parent_text
                    })
                    
                except Exception as e:
                    self.update_results(f"Error in fallback detection: {str(e)}\n")
                    
        except Exception as e:
            self.update_results(f"Fallback detection failed: {str(e)}\n")
        
        return products_data

    def process_product_diagrams(self, driver, product):
        """Process diagrams and specifications for a specific product in sequence."""
        self.update_results(f"\n--- Processing Product: {product['product_id']} ---\n")
        downloaded_something = False
        
        try:
            # Create directory for this product
            product_dir = os.path.join(self.output_dir, product['product_id'])
            diagram_dir = os.path.join(product_dir, config.DIAGRAM_FOLDER_NAME)
            os.makedirs(diagram_dir, exist_ok=True)
            
            # 1. Download Product Images (maximum 2 per product ID)
            if product.get('product_images'):
                self.update_results(f"Image: Attempting to download {min(2, len(product['product_images']))} images for {product['product_id']}...\n")
                downloaded_image_count = 0
                for img_el in product['product_images']:
                    if downloaded_image_count >= 2:
                        self.update_results("  Reached maximum of 2 product images, skipping further images.\n")
                        break
                    
                    try:
                        if self.download_product_image(driver, img_el, diagram_dir):
                            downloaded_something = True
                            downloaded_image_count += 1
                    except Exception as e:
                        self.update_results(f"  Error during product image download for one image: {str(e)}\n")
            else:
                self.update_results(f"  No product images found for {product['product_id']} with the current selector.\n")

            # 2. Process 商品図 (Product Diagram) - NO CHANGES TO THIS FUNCTIONALITY
            if product.get('diagram_link') or product.get('diagram_href'):
                try:
                    self.update_results(f"Diagram (商品図): Attempting to download for {product['product_id']}...\n")
                    if self.handle_diagram_download(driver, product, diagram_dir):
                        downloaded_something = True
                except Exception as e:
                    self.update_results(f"  Error downloading diagram: {str(e)}\n")
            else:
                self.update_results(f"  No 商品図 link found for {product['product_id']}.\n")
            
            # 3. Process 仕様一覧 (Specifications)
            if product.get('specs_link') or product.get('specs_href'):
                try:
                    self.update_results(f"Specifications (仕様一覧): Attempting to process for {product['product_id']}...\n")
                    specs_html = self.extract_specifications(driver, product.get('specs_link'), product.get('specs_href'), product['product_id'])
                    if specs_html:
                        specs_file = os.path.join(product_dir, f"{product['product_id']}_specifications.html")
                        with open(specs_file, 'w', encoding='utf-8') as f:
                            f.write(specs_html)
                        self.update_results(f"  Specifications saved: {specs_file}\n")
                        downloaded_something = True
                except Exception as e:
                    self.update_results(f"  Error processing specifications: {str(e)}\n")
            else:
                self.update_results(f"  No 仕様一覧 link found for {product['product_id']}.\n")
            
            return downloaded_something
                
        except Exception as e:
            self.update_results(f"  Error processing product: {str(e)}\n")
            return False

    def handle_diagram_download(self, driver, product, diagram_dir):
        """Refactored logic to handle clicking and downloading a diagram."""
        downloaded = False
        link_element = product.get('diagram_link')
        href = product.get('diagram_href')
        if not href and link_element:
            href = link_element.get_attribute('href')
        
        if href:
            self.update_results(f"  Link href: {href}\n")

        # First, try direct download if the href is a PDF link
        if href and href.lower().endswith('.pdf'):
            self.update_results("  Direct PDF link found, attempting direct download.\n")
            if self.download_file(href, diagram_dir):
                return True

        # If it's not a direct link or direct download fails, try clicking
        if link_element:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", link_element)
                time.sleep(1)
                
                current_window = driver.current_window_handle
                link_element.click()
                time.sleep(3) # Wait for action to complete

                # Check if a new tab was opened
                if len(driver.window_handles) > 1:
                    new_window = [h for h in driver.window_handles if h != current_window][0]
                    driver.switch_to.window(new_window)
                    self.update_results("  New tab detected for diagram.\n")
                    if self.download_from_current_page(driver, diagram_dir, pdf_only=True, single_file=True):
                        downloaded = True
                    driver.close()
                    driver.switch_to.window(current_window)
                else:
                    # No new tab, check if same page loaded the content
                    self.update_results("  No new tab, checking current page for diagram.\n")
                    if self.download_from_current_page(driver, diagram_dir, pdf_only=True, single_file=True):
                        downloaded = True
            except Exception as e:
                self.update_results(f"  Clicking diagram link failed: {e}\n")
        
        return downloaded

    def download_from_current_page(self, driver, diagram_dir, pdf_only=False, single_file=False):
        """Download diagrams from the current page."""
        try:
            self.update_results(f"  Analyzing current page for downloads...\n")
            current_url = driver.current_url
            time.sleep(2)

            # Method 1: If the current URL is a direct link to a file
            file_extensions = ['.pdf'] if pdf_only else ['.pdf', '.jpg', '.jpeg', '.png', '.gif']
            if any(ext in current_url.lower() for ext in file_extensions):
                filename = self.download_file_with_selenium(driver, diagram_dir)
                if filename:
                    self.update_results(f"  Successfully downloaded current page: {filename}\n")
                    return True

            # Method 2: Look for download links on the current page
            links_to_download = []
            all_links = driver.find_elements(By.TAG_NAME, "a")
            for link in all_links:
                href = link.get_attribute('href')
                if href and any(href.lower().endswith(ext) for ext in file_extensions):
                    links_to_download.append(href)

            self.update_results(f"  Found {len(links_to_download)} potential file links on this page.\n")

            for i, link_url in enumerate(links_to_download):
                self.update_results(f"  Attempting download from link {i+1}: {link_url}\n")
                if self.download_file(link_url, diagram_dir):
                    if single_file:
                        return True
            
            return False
            
        except Exception as e:
            self.update_results(f"  Error downloading from current page: {str(e)}\n")
            return False

    def download_file_with_selenium(self, driver, directory):
        """Download file using Selenium, deriving the filename from the URL."""
        try:
            current_url = driver.current_url
            
            # Get filename from URL
            parsed_url = urlparse(current_url)
            filename = os.path.basename(parsed_url.path)
            
            # If filename is empty or invalid, create one
            if not filename or '.' not in filename:
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
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{int(time.time())}{ext}"
                filepath = os.path.join(directory, filename)

            # Use asynchronous fetch in JS, which is more reliable
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
            
            # Use execute_async_script for promise-based JS
            driver.set_script_timeout(30)
            result = driver.execute_async_script(js_code, current_url)
            
            if isinstance(result, dict) and 'error' in result:
                self.update_results(f"    Selenium download via JS failed: {result['error']}\n")
                return None

            file_content = bytes(result)
            with open(filepath, 'wb') as f:
                f.write(file_content)
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                self.update_results(f"    Successfully downloaded via Selenium: {filename}\n")
                return filename
            else:
                self.update_results(f"    Selenium download failed - file is empty\n")
                if os.path.exists(filepath): os.remove(filepath)
                return None
                
        except Exception as e:
            self.update_results(f"    Error in Selenium download: {str(e)}\n")
            return None

    def extract_specifications(self, driver, specs_link, specs_href, product_id):
        """Extract specifications table and convert to Rakuten HTML format"""
        try:
            # Click the specifications link
            try:
                if specs_link is not None:
                    driver.execute_script("arguments[0].scrollIntoView(true);", specs_link)
                    time.sleep(1)
                    specs_link.click()
                    time.sleep(3)
                elif specs_href:
                    driver.get(specs_href)
                    time.sleep(3)
                else:
                    self.update_results("    No specifications link or URL available\n")
                    return None
            except Exception as e:
                self.update_results(f"    Error clicking specs link: {str(e)}\n")
                return None
            
            current_window = driver.current_window_handle
            if len(driver.window_handles) > 1:
                new_window = [h for h in driver.window_handles if h != current_window][0]
                driver.switch_to.window(new_window)
            
            time.sleep(2)
            
            specs_table = None
            table_selectors = ["[class*='spec'] table", "[class*='table']", "table"]
            
            for selector in table_selectors:
                try:
                    tables = driver.find_elements(By.CSS_SELECTOR, selector)
                    for table in tables:
                        if any(k in table.text for k in ['基本情報', '仕様', '質量', '発売時期']):
                            specs_table = table
                            break
                    if specs_table:
                        break
                except:
                    continue
            
            if not specs_table:
                self.update_results(f"    No specifications table found\n")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(current_window)
                return None
            
            table_data = self.extract_table_data(specs_table)
            rakuten_html = self.generate_rakuten_html(table_data, product_id)
            
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(current_window)
            
            return rakuten_html
            
        except Exception as e:
            self.update_results(f"    Error extracting specifications: {str(e)}\n")
            try:
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(current_window)
            except:
                pass
            return None

    def extract_table_data(self, table_element):
        """Extract data from specifications table"""
        table_data = []
        try:
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            current_section = ""
            for row in rows:
                try:
                    headers = row.find_elements(By.TAG_NAME, "th")
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if headers and len(cells) == 0:
                        current_section = headers[0].text.strip()
                    elif headers and cells:
                        item_name = headers[0].text.strip()
                        item_value = cells[0].text.strip()
                        if item_name and item_value:
                            table_data.append({'section': current_section, 'item': item_name, 'value': item_value})
                except:
                    continue
        except Exception as e:
            self.update_results(f"    Error extracting table data: {str(e)}\n")
        return table_data

    def generate_rakuten_html(self, table_data, product_id):
        """Generate HTML for Rakuten EC site based on specifications data"""
        try:
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{product_id} - 商品仕様</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        .section-title {{ background-color: #007bff; color: white; padding: 10px; font-weight: bold; border-radius: 4px; margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f8f9fa; font-weight: bold; width: 30%; }}
        .product-info {{ background-color: #e9ecef; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
        .product-id {{ font-size: 18px; font-weight: bold; color: #007bff; }}
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
                    html_content += f"        <div class=\"section-title\">{section}</div>\n        <table>\n"
                    last_section = section
                
                item_name = item['item'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                item_value = item['value'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html_content += f"            <tr><th>{item_name}</th><td>{item_value}</td></tr>\n"

            if last_section is not None:
                html_content += "        </table>\n"
            
            html_content += """
    </div>
</body>
</html>"""
            return html_content
        except Exception as e:
            self.update_results(f"    Error generating Rakuten HTML: {str(e)}\n")
            return None

    def download_direct_link(self, diagram, product_id):
        """Download a diagram from a direct link"""
        try:
            self.update_results(f"Downloading direct link: {diagram['text']}\n")
            
            # Create directory structure
            product_dir = os.path.join(self.output_dir, product_id)
            diagram_dir = os.path.join(product_dir, config.DIAGRAM_FOLDER_NAME)
            
            os.makedirs(diagram_dir, exist_ok=True)
            
            # Download the file
            filename = self.download_file(diagram['url'], diagram_dir)
            if filename:
                self.update_results(f"  Downloaded: {filename}\n")
                return True
            else:
                self.update_results(f"  Failed to download: {diagram['url']}\n")
                return False
                
        except Exception as e:
            self.update_results(f"  Error downloading direct link: {str(e)}\n")
            return False

    def process_product_page(self, driver, product, product_id):
        try:
            self.update_results(f"Processing product page: {product['text']}\n")
            
            # Navigate to product page
            driver.get(product['url'])
            time.sleep(config.PAGE_LOAD_TIMEOUT)
            
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
                self.update_results(f"  No diagrams found for {product['text']}\n")
                return False
            
            # Create directory structure
            product_dir = os.path.join(self.output_dir, product_id)
            diagram_dir = os.path.join(product_dir, config.DIAGRAM_FOLDER_NAME)
            
            os.makedirs(diagram_dir, exist_ok=True)
            
            # Download diagrams
            downloaded = False
            for diagram in diagram_links:
                try:
                    filename = self.download_file(diagram['url'], diagram_dir)
                    if filename:
                        self.update_results(f"  Downloaded: {filename}\n")
                        downloaded = True
                except Exception as e:
                    self.update_results(f"  Failed to download {diagram['url']}: {str(e)}\n")
            
            return downloaded
            
        except Exception as e:
            self.update_results(f"  Error processing page: {str(e)}\n")
            return False
    
    def download_file(self, url, directory):
        try:
            self.update_results(f"    Downloading from URL: {url}\n")
            
            # Get filename from URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # Clean up filename
            if filename:
                # Remove query parameters
                filename = filename.split('?')[0]
                # Remove any invalid characters
                filename = "".join(c for c in filename if c.isalnum() or c in "._-")
            
            if not filename or '.' not in filename:
                # Generate filename based on content type
                try:
                    headers = self.get_browser_headers()
                    response = requests.head(url, headers=headers, timeout=config.DOWNLOAD_TIMEOUT)
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
                        filename = f"file_{int(time.time())}.dat" # Fallback
                except:
                    filename = f"file_{int(time.time())}.dat"
            
            filepath = os.path.join(directory, filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{int(time.time())}{ext}"
                filepath = os.path.join(directory, filename)
            
            # Download file with browser headers
            headers = self.get_browser_headers()
            response = requests.get(url, headers=headers, timeout=config.DOWNLOAD_TIMEOUT, stream=True)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if 'text/html' in content_type:
                self.update_results("    Warning: Link leads to an HTML page, not a direct file. Skipping direct download.\n")
                return None
                
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=config.CHUNK_SIZE):
                    f.write(chunk)
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                self.update_results(f"    Successfully downloaded: {filename} ({os.path.getsize(filepath)} bytes)\n")
                return filename
            else:
                self.update_results(f"    File download failed - file is empty or missing\n")
                return None
            
        except Exception as e:
            self.update_results(f"    Download failed: {str(e)}\n")
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

    def download_product_image(self, driver, image_element, diagram_dir):
        """Click a thumbnail, then find and download the full-size image."""
        try:
            original_src = image_element.get_attribute('src')
            driver.execute_script("arguments[0].scrollIntoView(true);", image_element)
            time.sleep(1)
            current_window = driver.current_window_handle
            existing_handles = set(driver.window_handles)

            # Click the thumbnail to trigger the large image view
            try:
                image_element.click()
                time.sleep(2) # Wait for lightbox or new tab
            except Exception as e:
                self.update_results(f"    Could not click product image: {e}\n")
                return False

            # Case 1: A new tab opened with the large image.
            new_handles = set(driver.window_handles) - existing_handles
            if new_handles:
                self.update_results("    New tab detected, switching to download large image...\n")
                new_window = list(new_handles)[0]
                driver.switch_to.window(new_window)
                time.sleep(1)
                filename = self.download_file_with_selenium(driver, diagram_dir)
                driver.close()
                driver.switch_to.window(current_window)
                return filename is not None

            # Case 2: The click caused a lightbox/overlay to appear on the same page.
            try:
                self.update_results("    No new tab; searching for a lightbox image on the current page...\n")
                time.sleep(1) # Extra wait for lightbox to render
                all_images_on_page = driver.find_elements(By.TAG_NAME, "img")
                
                best_image_src = None
                max_area = 0

                for img in all_images_on_page:
                    if not img.is_displayed():
                        continue
                    
                    img_src = img.get_attribute('src')
                    if img_src == original_src:
                        continue
                        
                    try:
                        width = driver.execute_script("return arguments[0].naturalWidth;", img)
                        height = driver.execute_script("return arguments[0].naturalHeight; ", img)
                        area = width * height
                        
                        if area > max_area:
                            max_area = area
                            best_image_src = img_src
                    except Exception:
                        continue
                
                if best_image_src:
                    self.update_results(f"    Found large image in lightbox: {best_image_src}\n")
                    if self.download_file(best_image_src, diagram_dir):
                        return True
            except Exception as e:
                self.update_results(f"    Error while searching for lightbox image: {e}\n")

            self.update_results("    Could not find a larger image after clicking. Download failed.\n")
            return False
        except Exception as e:
            self.update_results(f"    An unexpected error occurred in download_product_image: {e}\n")
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
