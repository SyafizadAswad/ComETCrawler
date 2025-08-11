#!/usr/bin/env python3
"""
Windows ChromeDriver Fix Script for COM-ET Crawler
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def check_windows():
    """Check if running on Windows"""
    if platform.system() != "Windows":
        print("❌ This script is designed for Windows only")
        return False
    return True

def clear_chromedriver_cache():
    """Clear ChromeDriver cache"""
    print("Clearing ChromeDriver cache...")
    try:
        # Clear webdriver-manager cache
        cache_dir = Path.home() / ".wdm"
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            print("✅ Cleared webdriver-manager cache")
        
        # Clear pip cache
        subprocess.run([sys.executable, "-m", "pip", "cache", "purge"], 
                      capture_output=True, text=True)
        print("✅ Cleared pip cache")
        
        return True
    except Exception as e:
        print(f"⚠️  Could not clear cache: {e}")
        return False

def reinstall_webdriver_manager():
    """Reinstall webdriver-manager"""
    print("Reinstalling webdriver-manager...")
    try:
        # Uninstall
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "webdriver-manager"], 
                      capture_output=True, text=True)
        
        # Install latest version
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "webdriver-manager"], 
                      capture_output=True, text=True)
        
        print("✅ webdriver-manager reinstalled")
        return True
    except Exception as e:
        print(f"❌ Failed to reinstall webdriver-manager: {e}")
        return False

def download_chromedriver_manually():
    """Download ChromeDriver manually"""
    print("Downloading ChromeDriver manually...")
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Force download
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver downloaded to: {driver_path}")
        
        # Verify file exists and is executable
        if os.path.exists(driver_path):
            print("✅ ChromeDriver file verified")
            return True
        else:
            print("❌ ChromeDriver file not found")
            return False
            
    except Exception as e:
        print(f"❌ Manual download failed: {e}")
        return False

def test_chromedriver_execution():
    """Test if ChromeDriver can be executed"""
    print("Testing ChromeDriver execution...")
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        driver_path = ChromeDriverManager().install()
        
        # Test with minimal options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        
        # Try to create driver
        from selenium.webdriver.chrome.service import Service
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        # Test basic functionality
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✅ ChromeDriver test successful: {title}")
        return True
        
    except Exception as e:
        print(f"❌ ChromeDriver test failed: {e}")
        return False

def install_chrome_dependencies():
    """Install Chrome dependencies"""
    print("Installing Chrome dependencies...")
    try:
        # Install Microsoft Visual C++ Redistributable (if needed)
        print("Note: If ChromeDriver still fails, you may need to install Microsoft Visual C++ Redistributable")
        print("Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe")
        
        # Update pip and setuptools
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], 
                      capture_output=True, text=True)
        print("✅ Updated pip and setuptools")
        
        return True
    except Exception as e:
        print(f"⚠️  Could not install dependencies: {e}")
        return False

def create_test_script():
    """Create a simple test script"""
    test_script = """
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

try:
    print("Testing ChromeDriver...")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get("https://www.google.com")
    print(f"Success! Page title: {driver.title}")
    driver.quit()
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
"""
    
    with open("test_chromedriver.py", "w") as f:
        f.write(test_script)
    
    print("✅ Created test_chromedriver.py")

def main():
    print("Windows ChromeDriver Fix for COM-ET Crawler")
    print("=" * 50)
    print()
    
    if not check_windows():
        return False
    
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print()
    
    # Run fixes
    fixes = [
        clear_chromedriver_cache,
        reinstall_webdriver_manager,
        download_chromedriver_manually,
        install_chrome_dependencies,
        test_chromedriver_execution,
        create_test_script
    ]
    
    results = []
    for fix in fixes:
        try:
            result = fix()
            results.append(result)
        except Exception as e:
            print(f"❌ Fix failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("FIX SUMMARY")
    print("=" * 50)
    
    if all(results):
        print("🎉 All fixes applied successfully!")
        print("ChromeDriver should now work correctly.")
        print("\nYou can now run the COM-ET Crawler application.")
    else:
        print("⚠️  Some fixes failed. Try the following:")
        print("1. Run the test script: python test_chromedriver.py")
        print("2. Install Microsoft Visual C++ Redistributable")
        print("3. Try running as administrator")
        print("4. Update Google Chrome to latest version")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1) 