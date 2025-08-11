# COM-ET Product Diagram Downloader

A Python-based desktop application that automatically crawls the COM-ET website (https://www.com-et.com/jp/) and downloads product diagrams based on product IDs.

## Features

✅ **User-Friendly GUI**: Simple interface with product ID input and search button
✅ **Automated Web Crawling**: Uses Selenium with ChromeDriver for headless browser automation
✅ **Smart Search**: Automatically finds and uses the search functionality on the COM-ET website
✅ **Product Diagram Detection**: Searches for 「商品図」 (product diagram) sections on product pages
✅ **File Download**: Downloads PDF and image files from product pages
✅ **Organized Storage**: Creates structured directory hierarchy for downloaded files
✅ **Real-time Progress**: Shows search progress and download status
✅ **Error Handling**: Comprehensive error handling and user feedback

## Directory Structure

The application creates the following directory structure for downloaded files:

```
output/
└── [Product ID]/
    └── 商品図/
        └── [PDF or image files]
```

## Installation

### Prerequisites

- Python 3.7 or higher
- Google Chrome browser (for ChromeDriver)

### Step 1: Clone or Download

Download the application files to your local machine.

### Step 2: Set Up Virtual Environment

**For Windows users:**
```bash
# Use the setup script (recommended)
setup_venv.bat

# Or manual setup
python -m venv venv
venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
```

**For Unix/Linux/Mac users:**
```bash
# Use the setup script (recommended)
chmod +x setup_venv.sh
./setup_venv.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Run the Application

**Windows:**
```bash
# Use the run script (recommended)
run_crawler_venv.bat

# Or manual activation and run
venv\Scripts\activate.bat
python com_et_crawler.py
```

**Unix/Linux/Mac:**
```bash
# Use the run script (recommended)
chmod +x run_crawler_venv.sh
./run_crawler_venv.sh

# Or manual activation and run
source venv/bin/activate
python com_et_crawler.py
```

## Usage

1. **Launch the Application**: Run the Python script to open the GUI
2. **Enter Product ID**: Type the product ID you want to search for in the input field
3. **Start Search**: Click "Search & Download" or press Enter
4. **Monitor Progress**: Watch the progress bar and status updates
5. **View Results**: Check the results text area for detailed information
6. **Access Downloads**: Find downloaded files in the `output/` directory

## How It Works

1. **Website Navigation**: The application opens the COM-ET website in a headless Chrome browser
2. **Search Automation**: Automatically locates the search input field and enters the product ID
3. **Result Parsing**: Analyzes the search results page to find product links
4. **Product Page Processing**: Visits each product page to look for 「商品図」 sections
5. **File Detection**: Identifies downloadable files (PDFs, images) in the product diagram sections
6. **Download Management**: Downloads files to the organized directory structure

## Supported File Types

- PDF files (.pdf)
- Image files (.jpg, .jpeg, .png, .gif, .bmp, .tiff)

## Troubleshooting

### Common Issues

1. **ChromeDriver Issues**: The application automatically downloads and manages ChromeDriver. If you encounter issues:
   - Ensure Google Chrome is installed and up to date
   - Run the Windows fix script: `python fix_chromedriver_windows.py`
   - Run the troubleshooting script: `python troubleshoot_chrome.py`
   - Try running the application as administrator
   - Install Microsoft Visual C++ Redistributable if needed

2. **No Search Results**: If no products are found, the product ID might not exist or the website structure may have changed.

3. **Download Failures**: Some files might be protected or require authentication. The application will report failed downloads in the results.

4. **Slow Performance**: The application includes delays to respect the website and avoid being blocked. This is normal behavior.

5. **Virtual Environment Issues**: If you have trouble with virtual environments:
   - Ensure Python 3.7+ is installed
   - Try running `python -m venv --help` to verify venv is available
   - On some systems, you may need to install `python3-venv` package

6. **Package Installation Issues**: The application uses only pure Python packages to avoid compilation issues:
   - No C/C++ compilation tools required
   - Uses built-in HTML parser instead of lxml
   - All dependencies are cross-platform compatible

### Error Messages

- **"Could not find search input field"**: The website structure may have changed
- **"No product pages found"**: The search returned no results for the given product ID
- **"Download failed"**: The file URL is invalid or requires authentication

## Technical Details

- **Browser**: Chrome (headless mode)
- **Web Framework**: Selenium WebDriver
- **HTML Parsing**: BeautifulSoup4
- **GUI Framework**: tkinter (built-in Python)
- **File Downloads**: requests library with streaming support
- **Dependencies**: selenium, webdriver-manager, requests, beautifulsoup4

## Legal Notice

This application is for educational and personal use only. Please respect the COM-ET website's terms of service and robots.txt file. The application includes appropriate delays to avoid overwhelming the server.

## License

This project is provided as-is for educational purposes. Use responsibly and in accordance with the target website's terms of service. 