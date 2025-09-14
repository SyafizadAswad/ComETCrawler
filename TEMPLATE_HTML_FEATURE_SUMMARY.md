# Template HTML Generation Feature

## Overview
Enhanced the COM-ET crawler to generate product-specific HTML files following the template structure provided in `ref/toto-tcf5831adyr-sc1.html`.

## Key Changes Made

### 1. New HTML Generation Function
- **Function**: `generate_template_html()`
- **Purpose**: Creates HTML files that follow the exact template structure
- **Features**:
  - Product-specific information (manufacturer, product name, series)
  - Dynamic 仕様一覧 (specifications) table generation
  - Component information section (構成品)
  - Features categorization (洗浄機能, 快適機能, エコ機能, 清潔機能)

### 2. Enhanced Data Extraction
- **Function**: `extract_specifications_data()`
- **Purpose**: Extracts specifications data as structured data instead of pre-formatted HTML
- **Returns**: List of dictionaries with section, item, primary_value, and secondary_value

### 3. Helper Functions
- **`extract_manufacturer_from_product_id()`**: Determines manufacturer from product ID patterns
- **`extract_series_from_product_name()`**: Extracts series information from product names
- **`generate_specs_table_html()`**: Creates the specifications table in template format
- **`generate_features_html()`**: Categorizes and formats features by type

### 4. Updated Processing Flow
- Modified `process_product_diagrams()` to use the new template HTML generation
- Changed from generating `{product_id}_specifications.html` to `{product_id}_template.html`
- Integrated manufacturer and series detection

## Template Structure Features

### Product Information Section
```html
<!-- ●●●●● コメットから情報取得 -->
メーカー：TOTO（トートー）
品　番　：◆TCF5831ADYR#SC1
商品名　：ウォシュレットアプリコットP AP2A
シリーズ：パブリック向ウォシュレット
```

### Component Information Section
```html
<!-- ●●●●● コメットから情報取得 ●●●●● 構成品 -->
【 セット品番 ：TCF5831ADYR#SC1 】
構成品番 ： ◆TCF5831ADYR#SC1
商品名 ： ウォシュレットアプリコットP AP2A
```

### Specifications Table
- Black-bordered table with gray headers
- Handles special cases like rowspan for 吐水量
- Uses extracted 仕様一覧 data from COM-ET

### Features Section
- **洗浄機能**: Cleaning/washing features
- **快適機能**: Comfort features  
- **エコ機能**: Eco-friendly features
- **清潔機能**: Hygiene/cleanliness features

## Usage

The enhanced crawler now automatically generates template HTML files for each product processed. The files are saved as:
```
{output_dir}/{product_id}/{product_id}_template.html
```

## Benefits

1. **Consistent Format**: All generated HTML follows the same template structure
2. **Product-Specific**: Each HTML file is customized with the specific product information
3. **Automated**: No manual intervention required - works with existing scraping workflow
4. **Extensible**: Easy to add new features or modify the template structure

## Example Output

When processing a product like "TCF5831ADYR#SC1", the crawler will:
1. Extract specifications data from COM-ET
2. Determine manufacturer as "TOTO（トートー）" from product ID
3. Extract series as "パブリック向ウォシュレット" from product name
4. Generate a complete HTML file following the template structure
5. Save it as `TCF5831ADYR_SC1_template.html`

This enhancement makes the crawler much more useful for creating standardized product documentation that can be used directly in e-commerce or documentation systems.
