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
                elif option == "safebrowsing_disable_auto_update" and value:
                    chrome_options.add_argument("--safebrowsing-disable-auto-update")
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
                        minimal_options.add_argument("--disable-dev-shm-usage")
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
                            visible_options.add_argument("--disable-dev-shm-usage")
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
                            search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .search-button, .btn-search")
                            search_button.click()
                        except:
                            raise Exception(f"Could not interact with search field: {str(e)}")
                
                # Wait for search results to load
                self.update_status("Waiting for search results to load...")
                time.sleep(5)  # Give more time for dynamic content
                
                # Wait for search results to be visible
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
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
                for i, container in enumerate(product_containers):
                    try:
                        self.update_status(f"Processing product container {i+1}/{len(product_containers)}")
                        
                        # Extract product information from container
                        product_info = self.extract_product_info(container, driver)
                        
                        if product_info:
                            products_data.append(product_info)
                            self.update_results(f"Found product: {product_info['product_id']} - {product_info['product_name']}\n")
                        
                    except Exception as e:
                        self.update_results(f"Error processing container {i+1}: {str(e)}\n")
                
                if not products_data:
                    self.update_results("No products found in containers. Trying fallback method...\n")
                    # Fallback: try to find any 商品図 links on the page
                    products_data = self.fallback_product_detection(driver)
                
                self.update_status(f"Found {len(products_data)} products")
                self.update_results(f"Found {len(products_data)} products\n\n")
                
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
                self.update_status(f"Search completed. Downloaded {downloaded_count} diagrams.")
                self.update_results(f"\nSearch completed. Downloaded {downloaded_count} diagrams.\n")
                
            finally:
                driver.quit()
                
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.update_results(f"Error occurred: {str(e)}\n")
        finally:
            self.is_searching = False
            self.search_button.config(state='normal')
    
    def extract_product_info(self, container, driver):
        """Extract product information from a container element"""
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
            
            # Find 商品図 link within this container
            diagram_link = None
            try:
                # Look for 商品図 link within this container
                links = container.find_elements(By.TAG_NAME, "a")
                for link in links:
                    link_text = link.text.strip()
                    if '商品図' in link_text:
                        diagram_link = link
                        break
                
                # If not found, try to find by href
                if not diagram_link:
                    for link in links:
                        href = link.get_attribute('href')
                        if href and ('diagram' in href.lower() or 'drawing' in href.lower()):
                            diagram_link = link
                            break
            except:
                pass
            
            return {
                'product_id': product_id,
                'product_name': product_name,
                'container': container,
                'diagram_link': diagram_link,
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
        """Process diagrams for a specific product"""
        try:
            self.update_results(f"Processing diagrams for {product['product_id']}\n")
            
            # Create directory for this product
            product_dir = os.path.join(self.output_dir, product['product_id'])
            diagram_dir = os.path.join(product_dir, config.DIAGRAM_FOLDER_NAME)
            
            os.makedirs(diagram_dir, exist_ok=True)
            
            # Try to click the 商品図 link
            if product.get('diagram_link'):
                try:
                    self.update_results(f"  Clicking 商品図 link for {product['product_id']}\n")
                    
                    # Get the href before clicking
                    href = product['diagram_link'].get_attribute('href')
                    if href:
                        self.update_results(f"  Link href: {href}\n")
                    
                    # Scroll to the link
                    driver.execute_script("arguments[0].scrollIntoView(true);", product['diagram_link'])
                    time.sleep(1)
                    
                    # Try different click methods
                    clicked = False
                    
                    # Method 1: Regular click
                    try:
                        product['diagram_link'].click()
                        clicked = True
                        self.update_results(f"  Regular click successful\n")
                    except Exception as e:
                        self.update_results(f"  Regular click failed: {str(e)}\n")
                    
                    # Method 2: JavaScript click if regular click failed
                    if not clicked:
                        try:
                            driver.execute_script("arguments[0].click();", product['diagram_link'])
                            clicked = True
                            self.update_results(f"  JavaScript click successful\n")
                        except Exception as e:
                            self.update_results(f"  JavaScript click failed: {str(e)}\n")
                    
                    # Method 3: Direct download if it's a direct link
                    if href and any(ext in href.lower() for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.gif']):
                        self.update_results(f"  Direct download link detected\n")
                        filename = self.download_file(href, diagram_dir)
                        if filename:
                            self.update_results(f"  Direct download successful: {filename}\n")
                            return True
                    
                    if clicked:
                        time.sleep(3)
                        
                        # Handle potential new tab/window
                        current_window = driver.current_window_handle
                        if len(driver.window_handles) > 1:
                            # Switch to new tab
                            new_window = [handle for handle in driver.window_handles if handle != current_window][0]
                            driver.switch_to.window(new_window)
                            
                            self.update_results(f"  New tab opened, downloading from new tab\n")
                            # Download from new tab
                            downloaded = self.download_from_current_page(driver, diagram_dir, product['product_id'])
                            
                            # Close new tab and switch back
                            driver.close()
                            driver.switch_to.window(current_window)
                            
                            return downloaded
                        else:
                            # Download from same page
                            self.update_results(f"  No new tab, downloading from current page\n")
                            return self.download_from_current_page(driver, diagram_dir, product['product_id'])
                    else:
                        self.update_results(f"  All click methods failed\n")
                        return False
                        
                except Exception as e:
                    self.update_results(f"  Error clicking diagram link: {str(e)}\n")
                    return False
            else:
                self.update_results(f"  No diagram link found for {product['product_id']}\n")
                return False
                
        except Exception as e:
            self.update_results(f"  Error processing product diagrams: {str(e)}\n")
            return False

    def download_from_current_page(self, driver, diagram_dir, product_id):
        """Download diagrams from the current page"""
        try:
            self.update_results(f"  Analyzing current page for downloads...\n")
            
            # Get current page URL and title for debugging
            current_url = driver.current_url
            current_title = driver.title
            self.update_results(f"  Current URL: {current_url}\n")
            self.update_results(f"  Current title: {current_title}\n")
            
            # Wait a bit for page to load
            time.sleep(2)
            
            # Method 1: Try to download the current page if it's a direct file
            if any(ext in current_url.lower() for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.gif']):
                self.update_results(f"  Current page appears to be a direct file, attempting download...\n")
                filename = self.download_file_with_selenium(driver, diagram_dir)
                if filename:
                    self.update_results(f"  Successfully downloaded current page: {filename}\n")
                    return True
            
            # Method 2: Look for download links on the current page
            download_links = []
            
            # Look for direct file links
            file_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.zip']
            for ext in file_extensions:
                try:
                    links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{ext}')]")
                    download_links.extend(links)
                except:
                    continue
            
            # Look for download buttons
            download_texts = ['download', 'ダウンロード', 'Download', 'DOWNLOAD']
            for text in download_texts:
                try:
                    links = driver.find_elements(By.XPATH, f"//a[contains(text(), '{text}')]")
                    download_links.extend(links)
                except:
                    continue
            
            # Look for any links that might be downloads
            try:
                all_links = driver.find_elements(By.TAG_NAME, "a")
                for link in all_links:
                    href = link.get_attribute('href')
                    if href:
                        # Check if it looks like a download link
                        if any(ext in href.lower() for ext in file_extensions):
                            download_links.append(link)
                        elif 'download' in href.lower() or 'file' in href.lower():
                            download_links.append(link)
            except:
                pass
            
            # Look for images that might be diagrams
            try:
                images = driver.find_elements(By.TAG_NAME, "img")
                for img in images:
                    src = img.get_attribute('src')
                    if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                        # Create a download link for this image
                        download_links.append({
                            'url': src,
                            'type': 'image'
                        })
            except:
                pass
            
            self.update_results(f"  Found {len(download_links)} potential download links\n")
            
            # Try to download from each link
            downloaded = False
            for i, link in enumerate(download_links):
                try:
                    if isinstance(link, dict):
                        # Direct URL (from image src)
                        href = link['url']
                        filename = self.download_file(href, diagram_dir)
                    else:
                        # Selenium element - try clicking it
                        href = link.get_attribute('href')
                        self.update_results(f"  Attempting to click download link {i+1}: {href}\n")
                        
                        # Try clicking the link to trigger download
                        try:
                            link.click()
                            time.sleep(2)
                            filename = self.download_file_with_selenium(driver, diagram_dir)
                        except:
                            # If clicking fails, try direct download
                            filename = self.download_file(href, diagram_dir)
                    
                    if filename:
                        self.update_results(f"  Successfully downloaded: {filename}\n")
                        downloaded = True
                    else:
                        self.update_results(f"  Failed to download: {href}\n")
                except Exception as e:
                    self.update_results(f"  Error downloading {href}: {str(e)}\n")
            
            # If no downloads found, try to get the page source and look for embedded content
            if not downloaded:
                self.update_results(f"  No direct downloads found, checking page source...\n")
                page_source = driver.page_source
                
                # Look for embedded PDFs or images
                import re
                pdf_patterns = [
                    r'src=["\']([^"\']*\.pdf)["\']',
                    r'href=["\']([^"\']*\.pdf)["\']',
                    r'url\(["\']?([^"\']*\.pdf)["\']?\)'
                ]
                
                for pattern in pdf_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    for match in matches:
                        try:
                            if match.startswith('http'):
                                full_url = match
                            else:
                                full_url = urljoin(current_url, match)
                            
                            self.update_results(f"  Found embedded PDF: {full_url}\n")
                            filename = self.download_file(full_url, diagram_dir)
                            if filename:
                                self.update_results(f"  Downloaded embedded PDF: {filename}\n")
                                downloaded = True
                        except Exception as e:
                            self.update_results(f"  Failed to download embedded PDF: {str(e)}\n")
            
            return downloaded
            
        except Exception as e:
            self.update_results(f"  Error downloading from current page: {str(e)}\n")
            return False

    def download_file_with_selenium(self, driver, directory):
        """Download file using Selenium (for cases where requests is blocked)"""
        try:
            # Get the current page source and try to extract the file
            current_url = driver.current_url
            
            # Try to get the file content using JavaScript
            js_code = """
            var xhr = new XMLHttpRequest();
            xhr.open('GET', arguments[0], false);
            xhr.setRequestHeader('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
            xhr.setRequestHeader('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8');
            xhr.setRequestHeader('Accept-Language', 'en-US,en;q=0.9,ja;q=0.8');
            xhr.setRequestHeader('Referer', 'https://www.com-et.com/jp/');
            xhr.send();
            return xhr.responseText;
            """
            
            try:
                file_content = driver.execute_script(js_code, current_url)
                
                # Generate filename
                filename = f"diagram_{int(time.time())}.pdf"
                if '.jpg' in current_url.lower() or '.jpeg' in current_url.lower():
                    filename = f"diagram_{int(time.time())}.jpg"
                elif '.png' in current_url.lower():
                    filename = f"diagram_{int(time.time())}.png"
                elif '.gif' in current_url.lower():
                    filename = f"diagram_{int(time.time())}.gif"
                
                filepath = os.path.join(directory, filename)
                
                # Save the file
                with open(filepath, 'wb') as f:
                    f.write(file_content.encode('utf-8') if isinstance(file_content, str) else file_content)
                
                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    self.update_results(f"    Successfully downloaded via Selenium: {filename}\n")
                    return filename
                else:
                    self.update_results(f"    Selenium download failed - file is empty\n")
                    return None
                    
            except Exception as e:
                self.update_results(f"    Selenium download failed: {str(e)}\n")
                return None
                
        except Exception as e:
            self.update_results(f"    Error in Selenium download: {str(e)}\n")
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
            self.update_results(f"    Downloading: {url}\n")
            
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
                        filename = f"diagram_{int(time.time())}.{ext}"
                    else:
                        # Try to guess from URL
                        if '.pdf' in url.lower():
                            filename = f"diagram_{int(time.time())}.pdf"
                        elif any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                            for ext in ['.jpg', '.jpeg', '.png', '.gif']:
                                if ext in url.lower():
                                    filename = f"diagram_{int(time.time())}{ext}"
                                    break
                        else:
                            filename = f"diagram_{int(time.time())}.pdf"
                except:
                    filename = f"diagram_{int(time.time())}.pdf"
            
            filepath = os.path.join(directory, filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                filename = f"{os.path.splitext(filename)[0]}_{int(time.time())}{os.path.splitext(filename)[1]}"
                filepath = os.path.join(directory, filename)
            
            # Download file with browser headers
            self.update_results(f"    Saving to: {filepath}\n")
            headers = self.get_browser_headers()
            response = requests.get(url, headers=headers, timeout=config.DOWNLOAD_TIMEOUT, stream=True)
            response.raise_for_status()
            
            # Check if response is actually a file
            content_type = response.headers.get('content-type', '')
            content_length = response.headers.get('content-length', '0')
            
            self.update_results(f"    Content-Type: {content_type}, Size: {content_length} bytes\n")
            
            # Only download if it looks like a file
            if (any(ext in content_type.lower() for ext in ['pdf', 'image', 'application']) or
                int(content_length) > 1000):  # Files should be larger than 1KB
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=config.CHUNK_SIZE):
                        f.write(chunk)
                
                # Verify file was downloaded
                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    self.update_results(f"    Successfully downloaded: {filename} ({os.path.getsize(filepath)} bytes)\n")
                    return filename
                else:
                    self.update_results(f"    File download failed - file is empty or missing\n")
                    return None
            else:
                self.update_results(f"    Skipping - doesn't appear to be a file (Content-Type: {content_type})\n")
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