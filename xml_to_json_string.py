#!/usr/bin/env python3
"""
Script to read an XML file and output a JSON-escaped string for embedding as a value (e.g., for config.xml_content).
Usage:
    python xml_to_json_string.py pizzinifile.xml
"""
import sys
import json

if len(sys.argv) not in (2, 3):
    print("Usage: python xml_to_json_string.py <xml_file> [output_file]")
    sys.exit(1)

xml_path = sys.argv[1]
output_path = sys.argv[2] if len(sys.argv) == 3 else None

with open(xml_path, 'r', encoding='utf-8') as f:
    xml_content = f.read()

# Use json.dumps to escape the string for JSON, but remove the surrounding quotes
json_escaped = json.dumps(xml_content, ensure_ascii=False)
json_escaped_value = json_escaped[1:-1]

if output_path:
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(json_escaped_value)
    print(f"JSON-escaped XML content written to {output_path}")
else:
    print(json_escaped_value)
