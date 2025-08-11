#!/bin/bash

echo "COM-ET Product Diagram Downloader"
echo "================================="
echo ""

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Starting application..."
python com_et_crawler.py

echo ""
echo "Application closed." 