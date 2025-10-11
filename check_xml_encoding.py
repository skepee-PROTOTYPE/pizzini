"""Check XML file for encoding and special characters"""
import xml.etree.ElementTree as ET
from collections import Counter

print("Analyzing pizzinifile.xml for encoding issues...")
print()

# Read and parse the XML file
with open('pizzinifile.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# Parse XML
root = ET.fromstring(content)

# Find all pizzini entries
entries = []
special_chars = Counter()

for item in root.findall('.//pizzini'):
    title = item.find('Title')
    content_elem = item.find('Content')
    id_elem = item.find('Id')
    
    if title is None and content_elem is None:
        continue
    
    entry_id = id_elem.text if id_elem is not None else ""
    entry_content = content_elem.text if content_elem is not None else ""
    
    # Count special characters
    for char in entry_content:
        if ord(char) > 127:  # Non-ASCII
            special_chars[char] += 1
    
    entries.append({
        "id": entry_id,
        "content": entry_content[:100] + "..." if len(entry_content) > 100 else entry_content
    })

print(f"Total entries found: {len(entries)}")
print()

print("Most common special characters:")
for char, count in special_chars.most_common(20):
    print(f"  '{char}' (U+{ord(char):04X}): {count} times - {char.encode('unicode-escape').decode('ascii')}")

print()
print("First 5 entries preview:")
for i, entry in enumerate(entries[:5], 1):
    print(f"\n{i}. ID {entry['id']}: {entry['content']}")
