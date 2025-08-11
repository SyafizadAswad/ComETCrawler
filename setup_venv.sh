#!/bin/bash

echo "COM-ET Crawler Virtual Environment Setup"
echo "========================================"
echo ""

echo "Creating virtual environment..."
python3 -m venv venv

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Upgrading pip..."
pip install --upgrade pip

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Virtual environment setup complete!"
echo ""
echo "To run the application:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run the application: python com_et_crawler.py"
echo ""
echo "Or simply run: ./run_crawler_venv.sh"
echo "" 