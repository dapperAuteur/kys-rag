# tests/services/test_section_detector.py

import pytest
from app.services.section_detector import section_detector

@pytest.mark.asyncio
async def test_find_sections():
    """Test section detection with sample text."""
    sample_text = """
    Abstract
    This is the abstract.

    Introduction
    This is the introduction.

    Methods
    These are the methods.
    """
    
    sections = await section_detector.find_sections(sample_text)
    
    assert 'abstract' in sections
    assert 'introduction' in sections
    assert 'methods' in sections
    
    assert "This is the abstract" in sections['abstract']

@pytest.mark.asyncio
async def test_extract_tables():
    """Test table extraction."""
    sample_text = """
    Table 1: Sample Results
    Data | Value
    A    | 10
    B    | 20
    """
    
    tables = await section_detector.extract_tables(sample_text)
    
    assert len(tables) == 1
    assert tables[0]['caption'] == 'Sample Results'
    assert 'Data | Value' in tables[0]['content']