#!/usr/bin/env python3
"""
Test script to demonstrate the new template HTML generation functionality.
This script shows how the new generate_template_html function works with sample data.
"""

import sys
import os

# Add the current directory to the path so we can import the main module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from com_et_crawler import ComEtCrawler

def test_template_generation():
    """Test the new template HTML generation with sample data"""
    
    # Create a crawler instance (we won't use the GUI)
    crawler = ComEtCrawler()
    
    # Sample specifications data with proper hierarchical structure (similar to what would be extracted from COM-ET)
    sample_table_data = [
        # Regular items
        {'section': '基本情報', 'item': '発売時期', 'primary_value': '2025年08月', 'secondary_value': '', 'is_parent': False},
        {'section': '基本情報', 'item': '生産終了時期', 'primary_value': '-', 'secondary_value': '', 'is_parent': False},
        {'section': '基本情報', 'item': '便ふた有無', 'primary_value': '便ふた無し', 'secondary_value': '', 'is_parent': False},
        {'section': '基本情報', 'item': '便座形状(前丸便座・前割便座)', 'primary_value': '前丸便座', 'secondary_value': '', 'is_parent': False},
        {'section': '基本情報', 'item': '施工方式(上面施工・下面施工)', 'primary_value': '上面施工', 'secondary_value': '', 'is_parent': False},
        {'section': '基本情報', 'item': '着座センサ方式', 'primary_value': '静電容量方式', 'secondary_value': '', 'is_parent': False},
        {'section': '基本情報', 'item': '定格消費電力(W)', 'primary_value': '1261', 'secondary_value': '', 'is_parent': False},
        {'section': '基本情報', 'item': '熱交換器タンク方式', 'primary_value': '瞬間式', 'secondary_value': '', 'is_parent': False},
        {'section': '基本情報', 'item': '熱交換器タンク容量(貯湯式のみ)', 'primary_value': '-', 'secondary_value': '', 'is_parent': False},
        
        # Parent item with sub-items (吐水量)
        {'section': '基本情報', 'item': '吐水量(水圧0.2Mpa)', 'primary_value': '', 'secondary_value': '', 'is_parent': True, 'rowspan': 5},
        
        # Sub-items under 吐水量
        {'section': '基本情報', 'item': 'おしり洗浄', 'primary_value': '約0.27 ～ 0.43L/分', 'secondary_value': '', 'is_parent': False, 'parent_item': '吐水量(水圧0.2Mpa)'},
        {'section': '基本情報', 'item': 'おしりソフト洗浄', 'primary_value': '-', 'secondary_value': '', 'is_parent': False, 'parent_item': '吐水量(水圧0.2Mpa)'},
        {'section': '基本情報', 'item': 'やわらか洗浄', 'primary_value': '-', 'secondary_value': '', 'is_parent': False, 'parent_item': '吐水量(水圧0.2Mpa)'},
        {'section': '基本情報', 'item': 'ビデ洗浄', 'primary_value': '約0.29 ～ 0.43L/分', 'secondary_value': '', 'is_parent': False, 'parent_item': '吐水量(水圧0.2Mpa)'},
        {'section': '基本情報', 'item': 'ワイドビデ洗浄', 'primary_value': '-', 'secondary_value': '', 'is_parent': False, 'parent_item': '吐水量(水圧0.2Mpa)'},
        
        # More regular items
        {'section': '基本情報', 'item': 'ウォシュレット洗浄方式', 'primary_value': 'たっぷリッチ洗浄', 'secondary_value': '', 'is_parent': False},
        {'section': '基本情報', 'item': '便器洗浄水量(一体形シリーズ)', 'primary_value': '-', 'secondary_value': '', 'is_parent': False},
    ]
    
    # Test product information
    product_id = "TCF5831ADYR#SC1"
    product_name = "ウォシュレットアプリコットP AP2A"
    manufacturer = "TOTO（トートー）"
    series = "パブリック向ウォシュレット"
    
    print("Testing template HTML generation...")
    print(f"Product ID: {product_id}")
    print(f"Product Name: {product_name}")
    print(f"Manufacturer: {manufacturer}")
    print(f"Series: {series}")
    print(f"Specifications data entries: {len(sample_table_data)}")
    print()
    
    # Generate the template HTML
    template_html = crawler.generate_template_html(
        sample_table_data, 
        product_id, 
        product_name, 
        manufacturer, 
        series
    )
    
    if template_html:
        # Save the generated HTML to a file
        output_file = f"test_output_{product_id.replace('#', '_')}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(template_html)
        
        print(f"✅ Template HTML generated successfully!")
        print(f"📁 Output saved to: {output_file}")
        print(f"📊 HTML length: {len(template_html)} characters")
        
        # Show a preview of the generated HTML
        print("\n📋 HTML Preview (first 500 characters):")
        print("-" * 50)
        print(template_html[:500] + "..." if len(template_html) > 500 else template_html)
        print("-" * 50)
        
        return True
    else:
        print("❌ Template HTML generation failed!")
        return False

if __name__ == "__main__":
    print("🚀 COM-ET Crawler Template HTML Generation Test")
    print("=" * 60)
    
    success = test_template_generation()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("You can now open the generated HTML file in a browser to see the result.")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
