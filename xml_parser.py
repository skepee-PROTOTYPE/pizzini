"""
XML Parser for Pizzini Content
Reads and parses the pizzini XML file to extract social media content
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional
import re

class PizziniEntry:
    """Represents a single pizzini entry"""
    
    def __init__(self, entry_id: int, date: str, title: str, content: str):
        self.id = entry_id
        self.date = date
        self.title = title
        self.content = content
        self.parsed_date = self._parse_date(date)
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse the date string from the XML format"""
        try:
            # Handle the format "17.09.2012"
            return datetime.strptime(date_str, "%d.%m.%Y")
        except (ValueError, TypeError):
            return None
    
    def get_short_content(self, max_length: int = 200) -> str:
        """Get a shortened version of the content for social media"""
        if len(self.content) <= max_length:
            return self.content
        
        # Find a good breaking point (end of sentence)
        truncated = self.content[:max_length]
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        break_point = max(last_period, last_exclamation, last_question)
        
        if break_point > max_length * 0.7:  # If we found a good break point
            return self.content[:break_point + 1] + "..."
        else:
            return truncated + "..."
    
    def __str__(self):
        return f"Pizzini {self.id}: {self.title} ({self.date})"

class PizziniXMLParser:
    """Parser for the pizzini XML file"""
    
    def __init__(self, xml_file_path: str):
        self.xml_file_path = xml_file_path
        self.entries: List[PizziniEntry] = []
    
    def parse(self) -> List[PizziniEntry]:
        """Parse the XML file and return a list of PizziniEntry objects"""
        try:
            tree = ET.parse(self.xml_file_path)
            root = tree.getroot()
            
            # Find all pizzini elements (skip schema)
            pizzini_elements = root.findall('.//pizzini/pizzini')
            if not pizzini_elements:
                # Try alternative path structure
                pizzini_elements = root.findall('.//pizzini')
                # Filter out the schema element
                pizzini_elements = [elem for elem in pizzini_elements if elem.find('Id') is not None]
            
            for pizzini_elem in pizzini_elements:
                entry_id = self._get_element_text(pizzini_elem, 'Id', 0)
                date = self._get_element_text(pizzini_elem, 'Date', '')
                title = self._get_element_text(pizzini_elem, 'Title', '')
                content = self._get_element_text(pizzini_elem, 'Content', '')
                
                if title or content:  # Only add if we have meaningful content
                    entry = PizziniEntry(
                        entry_id=int(entry_id) if entry_id else 0,
                        date=date,
                        title=title,
                        content=content
                    )
                    self.entries.append(entry)
            
            return self.entries
            
        except ET.ParseError as e:
            print(f"Error parsing XML file: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    def _get_element_text(self, parent_elem, element_name: str, default='') -> str:
        """Safely get text from an XML element"""
        elem = parent_elem.find(element_name)
        return elem.text if elem is not None and elem.text else str(default)
    
    def get_entry_by_id(self, entry_id: int) -> Optional[PizziniEntry]:
        """Get a specific entry by its ID"""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None
    
    def get_all_entries(self) -> List[PizziniEntry]:
        """Get all parsed entries"""
        return self.entries

# Example usage and test
if __name__ == "__main__":
    parser = PizziniXMLParser("pizzini.xml")
    entries = parser.parse()
    
    print(f"Found {len(entries)} entries:")
    for entry in entries:
        print(f"\n{entry}")
        print(f"Short content: {entry.get_short_content(150)}")