"""Clean XML file by removing internal line breaks in content"""
import xml.etree.ElementTree as ET
import re

print("Cleaning pizzinifile.xml...")

# Read the XML file
with open('pizzinifile.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# Parse XML
tree = ET.ElementTree(ET.fromstring(content))
root = tree.getroot()

# Find all pizzini entries and clean content
cleaned_count = 0
for item in root.findall('.//pizzini'):
    content_elem = item.find('Content')
    
    if content_elem is not None and content_elem.text:
        original = content_elem.text
        
        # Replace multiple spaces/newlines with single space
        # Keep intentional paragraph breaks (double newlines) but remove line wrapping
        cleaned = re.sub(r'\n\s+', ' ', original)  # Replace newline + spaces with single space
        cleaned = re.sub(r'\s+', ' ', cleaned)  # Replace multiple spaces with single space
        cleaned = cleaned.strip()
        
        if cleaned != original:
            content_elem.text = cleaned
            cleaned_count += 1

print(f"Cleaned {cleaned_count} entries")

# Save the cleaned XML
# First, let's create a backup
import shutil
shutil.copy('pizzinifile.xml', 'pizzinifile.xml.backup')
print("Created backup: pizzinifile.xml.backup")

# Write cleaned XML
tree.write('pizzinifile_cleaned.xml', encoding='utf-8', xml_declaration=True)
print("Saved cleaned file: pizzinifile_cleaned.xml")

# Show sample before/after
print("\nSample comparison:")
with open('pizzinifile.xml', 'r', encoding='utf-8') as f:
    original_content = f.read()

with open('pizzinifile_cleaned.xml', 'r', encoding='utf-8') as f:
    cleaned_content = f.read()

# Find first entry with PATENTE
import_idx = original_content.find('PATENTE')
if import_idx > 0:
    sample_start = max(0, import_idx - 50)
    sample_end = min(len(original_content), import_idx + 200)
    
    print("\nORIGINAL:")
    print(repr(original_content[sample_start:sample_end]))
    
    import_idx_clean = cleaned_content.find('PATENTE')
    if import_idx_clean > 0:
        sample_start_clean = max(0, import_idx_clean - 50)
        sample_end_clean = min(len(cleaned_content), import_idx_clean + 200)
        
        print("\nCLEANED:")
        print(repr(cleaned_content[sample_start_clean:sample_end_clean]))
