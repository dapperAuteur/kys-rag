# tests/services/test_pdf_processor.py

import pytest
from pathlib import Path
from app.services.pdf_processor import PDFProcessor
import logging

# Set up logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def pdf_processor():
    """Create a PDF processor instance for testing."""
    return PDFProcessor()

@pytest.fixture
def sample_pdf_path(tmp_path):
    """Create a temporary path for test PDF."""
    return tmp_path / "test.pdf"

@pytest.mark.asyncio
async def test_extract_text_file_not_found(pdf_processor):
    """Test handling of non-existent PDF file."""
    with pytest.raises(FileNotFoundError):
        await pdf_processor.extract_text("nonexistent.pdf")

@pytest.mark.asyncio
async def test_get_metadata_file_not_found(pdf_processor):
    """Test handling of non-existent PDF file for metadata extraction."""
    with pytest.raises(FileNotFoundError):
        await pdf_processor.get_metadata("nonexistent.pdf")

@pytest.mark.asyncio
async def test_parse_pdf_date():
    """Test PDF date string parsing."""
    processor = PDFProcessor()
    
    # Test valid date
    assert processor._parse_pdf_date("D:20240110123456") is not None
    
    # Test invalid date
    assert processor._parse_pdf_date("invalid_date") is None

# Integration tests with real PDF files would go here
# Note: You'll need to add test PDF files to your test directory
