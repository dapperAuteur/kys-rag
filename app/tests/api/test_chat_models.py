# app/tests/api/test_chat_models.py

import pytest
from datetime import datetime, timezone
from app.models.responses.chat import (
    BaseResponse,
    FindingsResponse,
    ScientificStudyAnalysisResponse,
    ClaimResponse,
    ArticleAnalysisResponse,
    ErrorResponse
)

# We use this to create timestamps for our tests
def create_utc_datetime(year: int, month: int, day: int) -> datetime:
    """Create a datetime object in UTC timezone.
    
    This helps us make sure our dates are always in the same timezone,
    which prevents confusing test failures.
    """
    return datetime(year, month, day, tzinfo=timezone.utc)

class TestBaseResponse:
    """Tests for our basic response template.
    
    These tests make sure that every response includes the basic
    information we expect, like status and timestamp.
    """
    
    def test_valid_status(self):
        """Check that we only allow 'success' or 'error' as status."""
        # This should work fine - 'success' is a valid status
        response = BaseResponse(status="success")
        assert response.status == "success"
        
        # This should also work - 'error' is valid too
        response = BaseResponse(status="error")
        assert response.status == "error"
        
        # This should raise an error - 'invalid' is not a valid status
        with pytest.raises(ValueError):
            BaseResponse(status="invalid")
    
    def test_default_values(self):
        """Make sure we get the right default values."""
        response = BaseResponse()
        assert response.status == "success"  # Default status should be success
        assert isinstance(response.timestamp, datetime)  # Should have a timestamp
        assert isinstance(response.metadata, dict)  # Should have empty metadata

class TestFindingsResponse:
    """Tests for how we organize scientific findings.
    
    These tests check that we correctly store and validate the key
    information we extract from scientific studies.
    """
    
    def test_required_citation(self):
        """Check that we require a citation."""
        # This should fail because we didn't provide a citation
        with pytest.raises(ValueError):
            FindingsResponse()
        
        # This should work because we provided all required fields
        findings = FindingsResponse(citation="Smith et al., 2024")
        assert findings.citation == "Smith et al., 2024"
    
    def test_optional_fields(self):
        """Check that optional fields work correctly."""
        findings = FindingsResponse(
            citation="Smith et al., 2024",
            key_points=["Point 1", "Point 2"],
            methodology="Test method",
            limitations=["Limitation 1"]
        )
        assert len(findings.key_points) == 2
        assert findings.methodology == "Test method"
        assert len(findings.limitations) == 1

class TestScientificStudyAnalysisResponse:
    """Tests for our complete scientific study analysis.
    
    These tests verify that we can create a full analysis response
    with all the necessary information about a study.
    """
    
    def test_complete_response(self):
        """Test creating a complete analysis response."""
        findings = FindingsResponse(
            key_points=["Exercise improves sleep"],
            methodology="Random trial",
            limitations=["Small sample"],
            citation="Smith et al., 2024"
        )
        
        response = ScientificStudyAnalysisResponse(
            title="Sleep Study",
            findings=findings,
            relevant_section="Results section",
            confidence_score=0.95
        )
        
        assert response.content_type == "scientific_study"
        assert response.title == "Sleep Study"
        assert response.findings.key_points[0] == "Exercise improves sleep"
        assert response.confidence_score == 0.95
    
    def test_confidence_score_limits(self):
        """Make sure confidence scores stay between 0 and 1."""
        findings = FindingsResponse(citation="Test")
        
        # Score too high
        with pytest.raises(ValueError):
            ScientificStudyAnalysisResponse(
                title="Test",
                findings=findings,
                confidence_score=1.5
            )
        
        # Score too low
        with pytest.raises(ValueError):
            ScientificStudyAnalysisResponse(
                title="Test",
                findings=findings,
                confidence_score=-0.5
            )

class TestArticleAnalysisResponse:
    """Tests for article analysis responses.
    
    These tests check how we handle analyzing news articles
    and verifying their scientific claims.
    """
    
    def test_article_with_claims(self):
        """Test analyzing an article with multiple claims."""
        claims = [
            ClaimResponse(
                text="Claim 1",
                verified=True,
                confidence_score=0.9
            ),
            ClaimResponse(
                text="Claim 2",
                verified=False,
                confidence_score=0.8
            )
        ]
        
        response = ArticleAnalysisResponse(
            title="News Article",
            source="Science News",
            publication_date=create_utc_datetime(2024, 1, 15),
            claims=claims
        )
        
        assert response.content_type == "article"
        assert len(response.claims) == 2
        assert response.claims[0].verified
        assert not response.claims[1].verified

class TestErrorResponse:
    """Tests for error responses.
    
    These tests make sure we provide helpful error messages
    when something goes wrong.
    """
    
    def test_error_response_format(self):
        """Check that error responses have the right format."""
        error = ErrorResponse(
            code=404,
            message="Study not found",
            details={"study_id": "123"}
        )
        
        assert error.status == "error"  # Should always be "error"
        assert error.code == 404
        assert "not found" in error.message.lower()
        assert error.details["study_id"] == "123"