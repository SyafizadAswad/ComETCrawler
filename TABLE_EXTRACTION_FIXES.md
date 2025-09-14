# Table Extraction Fixes - Hierarchical Structure Support

## Problem Identified
The original table extraction was flattening the hierarchical structure of the specifications table, particularly with the "吐水量" (water discharge) section. This caused:

1. **Duplicated items**: Sub-items were being treated as separate top-level entries
2. **Lost hierarchy**: Parent-child relationships were not preserved
3. **Incorrect structure**: The generated HTML didn't match the original table format

## Root Cause
The `extract_table_data()` function was not properly handling:
- **Rowspan attributes**: Parent items with sub-items (like 吐水量 with rowspan=5)
- **Colspan attributes**: Headers spanning multiple columns
- **Parent-child relationships**: Sub-items under parent categories

## Solution Implemented

### 1. Enhanced Table Data Extraction (`extract_table_data()`)
- **Detects rowspan attributes**: Identifies parent items with sub-items
- **Preserves hierarchy**: Maintains parent-child relationships
- **Handles colspan**: Properly processes headers spanning multiple columns
- **Avoids duplicates**: Prevents sub-items from being treated as separate entries

### 2. Improved HTML Generation (`generate_specs_table_html()`)
- **Groups items by relationships**: Separates parent items from sub-items
- **Generates proper rowspan**: Creates correct HTML table structure
- **Maintains original format**: Matches the template structure exactly

### 3. Duplicate Prevention (`generate_features_html()`)
- **Filters sub-items**: Excludes sub-items from features section to avoid duplicates
- **Preserves main items**: Only includes top-level items in feature categorization

## Key Changes Made

### Table Data Structure
```python
# Before (flattened)
{'item': '吐水量', 'primary_value': '...', 'secondary_value': '...'}

# After (hierarchical)
{'item': '吐水量', 'is_parent': True, 'rowspan': 5, 'parent_item': None}
{'item': 'おしり洗浄', 'is_parent': False, 'parent_item': '吐水量'}
```

### HTML Generation Logic
```python
# Groups items by parent-child relationships
parent_items = []
sub_items = {}

# Processes parent items with proper rowspan
if item_name in sub_items and sub_items[item_name]:
    rowspan = len(sub_items[item_name]) + 1
    # Generate parent row with rowspan
    # Generate sub-item rows
```

## Expected Results

### Before Fix
- ❌ Duplicated items (おしり洗浄, ビデ洗浄, etc. appearing twice)
- ❌ Flattened structure (no parent-child relationships)
- ❌ Incorrect HTML table structure

### After Fix
- ✅ No duplicates (sub-items only appear under their parent)
- ✅ Proper hierarchy (吐水量 as parent with sub-items)
- ✅ Correct HTML table with rowspan attributes
- ✅ Matches original table structure exactly

## Technical Details

### Rowspan Detection
```python
rowspan = header_element.get_attribute("rowspan")
if rowspan and int(rowspan) > 1:
    # This is a parent item with sub-items
    parent_item = headers[0].text.strip()
```

### Sub-item Identification
```python
elif headers and cells and len(headers) == 2 and len(cells) == 1:
    # This is a sub-item under a parent
    sub_item_name = headers[1].text.strip()
    sub_item_value = cells[0].text.strip()
```

### HTML Generation
```html
<tr>
  <th rowspan="5" align="left" bgcolor="#F5F5F5">吐水量(水圧0.2Mpa)<br>ポンプ式の場合水圧は関係ありません</th>
  <th align="left" bgcolor="#F5F5F5">おしり洗浄</th>
  <td bgcolor="#FFFFFF" align="left">約0.27 ～ 0.43L/分</td>
</tr>
<tr>
  <th align="left" bgcolor="#F5F5F5">おしりソフト洗浄</th>
  <td bgcolor="#FFFFFF" align="left">-</td>
</tr>
<!-- ... more sub-items ... -->
```

## Testing
The updated extraction now properly handles:
- ✅ Parent items with rowspan attributes
- ✅ Sub-items under parent categories
- ✅ Regular items without hierarchy
- ✅ Proper HTML table generation
- ✅ No duplicate entries
- ✅ Correct template structure

This fix ensures that the generated HTML tables exactly match the original product specification tables from COM-ET, maintaining the proper hierarchical structure and avoiding any duplicate entries.
