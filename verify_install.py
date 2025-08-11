#!/usr/bin/env python3
"""
Quick verification script for COM-ET Crawler installation
"""

def main():
    print("COM-ET Crawler - Installation Verification")
    print("=" * 45)
    print()
    
    # Test essential imports
    try:
        import tkinter
        print("✅ tkinter (GUI framework)")
    except ImportError:
        print("❌ tkinter - GUI framework not available")
        return False
    
    try:
        import selenium
        print("✅ selenium (web automation)")
    except ImportError:
        print("❌ selenium - web automation not available")
        return False
    
    try:
        import requests
        print("✅ requests (HTTP library)")
    except ImportError:
        print("❌ requests - HTTP library not available")
        return False
    
    try:
        import bs4
        print("✅ beautifulsoup4 (HTML parsing)")
    except ImportError:
        print("❌ beautifulsoup4 - HTML parsing not available")
        return False
    
    print("✅ html.parser (built-in HTML processing)")
    
    try:
        import config
        print("✅ config (configuration file)")
    except ImportError:
        print("❌ config - configuration file not found")
        return False
    
    print()
    print("🎉 All dependencies are installed correctly!")
    print("You can now run: python com_et_crawler.py")
    return True

if __name__ == "__main__":
    main() 