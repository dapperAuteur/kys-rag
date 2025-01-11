import pytest
from app.services.vector_service import VectorService, ProcessingMetrics
import torch
import numpy as np

@pytest.fixture
def vector_service():
    """Create a VectorService instance for testing."""
    return VectorService()

class TestVectorService:
    """Test suite for VectorService functionality."""

    @pytest.mark.asyncio
    async def test_preprocess_text(self, vector_service):
        """Test text preprocessing functionality."""
        # Test with various text formats
        test_cases = [
            (
                "This is\na test\ttext  with   spaces",
                "This is a test text with spaces"
            ),
            (
                "\n\nExtra\n\nlines\n\n",
                "Extra lines"
            ),
            (
                "Text with\tnon-printable\x00characters",
                "Text with non-printable characters"
            )
        ]
        
        for input_text, expected in test_cases:
            result = await vector_service._preprocess_text(input_text)
            assert result == expected

    def test_chunk_text(self, vector_service):
        """Test text chunking functionality."""
        # Create a long text
        words = ["word"] * 1000
        text = " ".join(words)
        
        # Test with different chunk sizes
        chunk_sizes = [100, 200, 500]
        
        for size in chunk_sizes:
            chunks = vector_service._chunk_text(text, chunk_size=size)
            
            # Check that chunks are created
            assert len(chunks) > 0
            
            # Check chunk sizes
            for chunk in chunks:
                chunk_words = chunk.split()
                assert len(chunk_words) <= size
                
            # Check for overlap
            if len(chunks) > 1:
                first_chunk_words = set(chunks[0].split())
                second_chunk_words = set(chunks[1].split())
                overlap = first_chunk_words.intersection(second_chunk_words)
                assert len(overlap) > 0

    @pytest.mark.asyncio
    async def test_generate_chunk_embedding(self, vector_service):
        """Test chunk embedding generation."""
        test_text = "This is a test chunk for embedding generation."
        
        embedding = await vector_service._generate_chunk_embedding(test_text)
        
        # Check embedding properties
        assert isinstance(embedding, torch.Tensor)
        assert embedding.dim() == 2  # Should be 2D tensor
        assert embedding.size(0) == 1  # Batch size 1
        
        # Check normalization
        norm = torch.norm(embedding)
        assert torch.abs(norm - 1.0) < 1e-6  # Should be normalized

    @pytest.mark.asyncio
    async def test_generate_embedding(self, vector_service):
        """Test full embedding generation pipeline."""
        test_text = """
        This is a longer text that will test the full embedding generation pipeline.
        It includes multiple sentences and should be processed in chunks.
        The final embedding should capture the semantic meaning of the text.
        """
        
        embedding = await vector_service.generate_embedding(test_text)
        
        # Check embedding properties
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
        
        # Check metrics were recorded
        metrics = await vector_service.get_processing_metrics()
        assert len(metrics) > 0
        
        last_metric = list(metrics.values())[-1]
        assert isinstance(last_metric, ProcessingMetrics)
        assert last_metric.success
        assert last_metric.chunk_count > 0
        assert last_metric.processing_time > 0
        assert last_metric.input_length > 0

    @pytest.mark.asyncio
    async def test_calculate_similarity(self, vector_service):
        """Test similarity calculation between embeddings."""
        # Create test embeddings
        embedding1 = [1.0, 0.0, 0.0]  # Unit vector along x
        embedding2 = [0.0, 1.0, 0.0]  # Unit vector along y
        embedding3 = [1.0, 0.0, 0.0]  # Same as embedding1
        
        # Test orthogonal vectors (should have similarity 0)
        sim1 = await vector_service.calculate_similarity(embedding1, embedding2)
        assert abs(sim1 - 0.0) < 1e-6
        
        # Test identical vectors (should have similarity 1)
        sim2 = await vector_service.calculate_similarity(embedding1, embedding3)
        assert abs(sim2 - 1.0) < 1e-6
        
        # Test similarity is symmetric
        sim3 = await vector_service.calculate_similarity(embedding2, embedding1)
        assert abs(sim3 - sim1) < 1e-6

    @pytest.mark.asyncio
    async def test_error_handling(self, vector_service):
        """Test error handling in embedding generation."""
        # Test with invalid input
        invalid_inputs = [
            "",  # Empty string
            None,  # None
            "x" * 1000000  # Very long text
        ]
        
        for invalid_input in invalid_inputs:
            try:
                result = await vector_service.generate_embedding(invalid_input)
                assert result is None
            except Exception as e:
                # Check that error was recorded in metrics
                metrics = await vector_service.get_processing_metrics()
                last_metric = list(metrics.values())[-1]
                assert isinstance(last_metric, ProcessingMetrics)
                assert not last_metric.success
                assert last_metric.error_message != ""

    @pytest.mark.asyncio
    async def test_processing_metrics(self, vector_service):
        """Test that processing metrics are properly recorded."""
        # Process some test texts
        texts = [
            "This is the first test text.",
            "This is the second test text.",
            "This is the third test text."
        ]
        
        for text in texts:
            await vector_service.generate_embedding(text)
        
        # Get metrics
        metrics = await vector_service.get_processing_metrics()
        
        # Check metrics properties
        assert len(metrics) == len(texts)
        for text_id, metric in metrics.items():
            assert isinstance(metric, ProcessingMetrics)
            assert metric.chunk_count > 0
            assert metric.processing_time > 0
            assert metric.input_length > 0
            assert metric.success
            
    @pytest.mark.asyncio
    async def test_batch_processing(self, vector_service):
        """Test processing multiple texts in sequence."""
        # Create a batch of test texts
        texts = [
            "First text for batch processing test.",
            "Second text with different content.",
            "Third text to ensure consistent processing."
        ]
        
        # Process all texts
        embeddings = []
        for text in texts:
            embedding = await vector_service.generate_embedding(text)
            embeddings.append(embedding)
        
        # Check results
        assert len(embeddings) == len(texts)
        for embedding in embeddings:
            assert embedding is not None
            assert len(embedding) > 0
            
        # Calculate similarities between all pairs
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = await vector_service.calculate_similarity(
                    embeddings[i],
                    embeddings[j]
                )
                assert 0 <= similarity <= 1