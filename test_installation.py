#!/usr/bin/env python3
"""
Test script to verify COM-ET Crawler installation
"""

import sys
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    required_packages = [
        'tkinter',
        'selenium',
        'webdriver_manager',
        'requests',
        'bs4'
    ]
    
    print("Testing package imports...")
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    return failed_imports

def test_config():
    """Test if configuration file can be loaded"""
    try:
        import config
        print("✅ Configuration file loaded successfully")
        return True
    except ImportError as e:
        print(f"❌ Configuration file error: {e}")
        return False

def test_main_app():
    """Test if main application can be imported"""
    try:
        from com_et_crawler import ComEtCrawler
        print("✅ Main application can be imported")
        return True
    except ImportError as e:
        print(f"❌ Main application import error: {e}")
        return False

def main():
    print("COM-ET Crawler Installation Test")
    print("=" * 40)
    print()
    
    # Test Python version
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    else:
        print("✅ Python version is compatible")
    
    print()
    
    # Test imports
    failed_imports = test_imports()
    print()
    
    # Test configuration
    config_ok = test_config()
    print()
    
    # Test main app
    app_ok = test_main_app()
    print()
    
    # Summary
    print("Installation Test Summary:")
    print("=" * 30)
    
    if not failed_imports and config_ok and app_ok:
        print("✅ All tests passed! The application is ready to use.")
        print("\nTo run the application:")
        print("  python com_et_crawler.py")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        if failed_imports:
            print(f"\nMissing packages: {', '.join(failed_imports)}")
            print("Run: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 