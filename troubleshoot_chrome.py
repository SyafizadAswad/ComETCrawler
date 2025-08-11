#!/usr/bin/env python3
"""
ChromeDriver Troubleshooting Script for COM-ET Crawler
"""

import os
import sys
import subprocess
import platform

def check_chrome_installation():
    """Check if Google Chrome is installed"""
    print("Checking Google Chrome installation...")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome found at: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        print("❌ Google Chrome not found in common locations")
        print("Please install Google Chrome from: https://www.google.com/chrome/")
        return False
    
    return True

def check_chrome_version():
    """Check Chrome version"""
    try:
        import subprocess
        result = subprocess.run(['chrome', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Chrome version: {result.stdout.strip()}")
            return True
    except:
        pass
    
    print("⚠️  Could not determine Chrome version automatically")
    return True

def check_webdriver_manager():
    """Check webdriver-manager installation"""
    print("\nChecking webdriver-manager...")
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ webdriver-manager is installed")
        return True
    except ImportError:
        print("❌ webdriver-manager is not installed")
        print("Run: pip install webdriver-manager")
        return False

def test_chromedriver_download():
    """Test ChromeDriver download"""
    print("\nTesting ChromeDriver download...")
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        print("Downloading ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver downloaded to: {driver_path}")
        
        # Check if the file exists and is executable
        if os.path.exists(driver_path):
            print("✅ ChromeDriver file exists")
            return True
        else:
            print("❌ ChromeDriver file not found")
            return False
            
    except Exception as e:
        print(f"❌ ChromeDriver download failed: {str(e)}")
        return False

def test_selenium_import():
    """Test Selenium import"""
    print("\nTesting Selenium import...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("✅ Selenium imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Selenium import failed: {str(e)}")
        return False

def test_basic_driver_creation():
    """Test basic driver creation"""
    print("\nTesting basic driver creation...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Create minimal options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Try to create driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Driver created successfully")
        
        # Test basic functionality
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ Basic web navigation test passed: {title}")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Driver creation failed: {str(e)}")
        return False

def main():
    print("ChromeDriver Troubleshooting for COM-ET Crawler")
    print("=" * 50)
    print()
    
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print()
    
    # Run all checks
    checks = [
        check_chrome_installation,
        check_chrome_version,
        check_webdriver_manager,
        test_chromedriver_download,
        test_selenium_import,
        test_basic_driver_creation
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Check failed with error: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("TROUBLESHOOTING SUMMARY")
    print("=" * 50)
    
    if all(results):
        print("🎉 All checks passed! ChromeDriver should work correctly.")
        print("You can now run the COM-ET Crawler application.")
    else:
        print("❌ Some checks failed. Please address the issues above.")
        print("\nCommon solutions:")
        print("1. Install/update Google Chrome")
        print("2. Run: pip install --upgrade webdriver-manager selenium")
        print("3. Clear ChromeDriver cache: webdriver-manager --clean")
        print("4. Try running as administrator")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1) 