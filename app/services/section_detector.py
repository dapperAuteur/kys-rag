# app/services/section_detector.py

import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SectionDetector:
    """Detects and extracts sections from scientific paper text."""
    
    def __init__(self):
        # Common section headers in scientific papers
        self.section_patterns = {
            'abstract': r'abstract|summary',
            'introduction': r'introduction|background',
            'methods': r'methods|methodology|materials and methods',
            'results': r'results|findings',
            'discussion': r'discussion',
            'conclusion': r'conclusion|conclusions',
            'references': r'references|bibliography'
        }
        
        # Compile regular expressions for better performance
        self.section_regex = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.section_patterns.items()
        }
        
        logger.info("SectionDetector initialized with standard scientific paper sections")

    async def find_sections(self, text: str) -> Dict[str, str]:
        """
        Find and extract sections from paper text.
        
        Args:
            text: Complete paper text
            
        Returns:
            Dictionary of section names and their content
        """
        logger.info("Starting section detection")
        sections = {}
        
        # Split text into lines for analysis
        lines = text.split('\n')
        
        # Track current section while going through text
        current_section = None
        current_content = []
        
        for line in lines:
            # Check if this line starts a new section
            new_section = None
            for section_name, pattern in self.section_regex.items():
                if pattern.match(line.strip()):
                    new_section = section_name
                    break
            
            if new_section:
                # Save previous section if it exists
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                    logger.debug(f"Found {current_section} section with {len(current_content)} lines")
                
                # Start new section
                current_section = new_section
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Don't forget the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        logger.info(f"Found {len(sections)} sections: {', '.join(sections.keys())}")
        return sections

    async def extract_tables(self, text: str) -> List[Dict[str, str]]:
        """
        Find and extract tables from text.
        
        Args:
            text: Paper text
            
        Returns:
            List of dictionaries containing table caption and content
        """
        logger.info("Starting table extraction")
        tables = []
        
        # Look for common table markers
        table_pattern = re.compile(
            r'Table\s+\d+[.:]\s*([^\n]+)',
            re.IGNORECASE
        )
        
        matches = table_pattern.finditer(text)
        for match in matches:
            caption = match.group(1)
            # Get text following the caption until next section
            content_start = match.end()
            content_end = text.find('\n\n', content_start)
            if content_end == -1:
                content_end = len(text)
            
            content = text[content_start:content_end].strip()
            tables.append({
                'caption': caption,
                'content': content
            })
        
        logger.info(f"Found {len(tables)} tables")
        return tables

# Create singleton instance
section_detector = SectionDetector()