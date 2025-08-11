# Configuration file for COM-ET Product Diagram Downloader

# Website settings
WEBSITE_URL = "https://www.com-et.com/jp/"
SEARCH_TIMEOUT = 10  # seconds to wait for search results
PAGE_LOAD_TIMEOUT = 5  # seconds to wait for page loads

# Browser settings
BROWSER_OPTIONS = {
    "headless": False,  # Set to False for debugging
    "no_sandbox": True,
    "disable_dev_shm_usage": True,
    "disable_gpu": True,
    "window_size": "1920,1080",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "disable_extensions": True,
    "disable_plugins": True,
    "disable_web_security": True,
    "allow_running_insecure_content": True,
    "disable_background_networking": True,
    "disable_background_timer_throttling": True,
    "disable_client_side_phishing_detection": True,
    "disable_default_apps": True,
    "disable_hang_monitor": True,
    "disable_prompt_on_repost": True,
    "disable_sync": True,
    "metrics_recording_only": True,
    "no_first_run": True,
    "safebrowsing_disable_auto_update": True,
    "disable_software_rasterizer": True
}

# File download settings
DOWNLOAD_TIMEOUT = 30  # seconds for file downloads
CHUNK_SIZE = 8192  # bytes per chunk for streaming downloads
SUPPORTED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']

# Directory settings
OUTPUT_DIR = "output"
DIAGRAM_FOLDER_NAME = "商品図"

# Search patterns for finding product links
PRODUCT_LINK_PATTERNS = [
    "a[href*='product']",
    "a[href*='item']",
    "a[href*='detail']",
    ".product a",
    ".item a",
    "a[onclick*='product']"
]

# Search patterns for finding search input
SEARCH_INPUT_PATTERNS = [
    "input[type='text']",
    "input[placeholder*='検索']",
    "input[name*='search']",
    "input[id*='search']",
    ".search input",
    "#search input"
]

# GUI settings
GUI_TITLE = "COM-ET Product Diagram Downloader"
GUI_SIZE = "800x600"
GUI_BG_COLOR = "#f0f0f0"

# Logging settings
ENABLE_LOGGING = True
LOG_LEVEL = "INFO"
LOG_FILE = "crawler.log" 