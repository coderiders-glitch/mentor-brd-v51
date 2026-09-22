import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestSearchEndpoint:
    """Tests for the search API endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_harvest_api, mock_get_secret):
        """Setup test fixtures."""
        self.mock_api = mock_harvest_api
        self.mock_secret = mock_get_secret

    def test_search_success(self, client):
        """Test successful search returns results."""
        response = client.get("/api/search?query=John")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
        assert data["results"][0]["name"] == "John Doe"

    def test_search_empty_query(self, client):
        """Test search with empty query returns validation error."""
        response = client.get("/api/search")
        assert response.status_code == 422

    def test_search_with_malformed_api_key(self, client, mock_harvest_client):
        """Test search handles API errors gracefully."""
        # The mock is already set up by the fixture
        response = client.get("/api/search?query=John")
        assert response.status_code == 200

    def test_profile_success(self, client):
        """Test successful profile fetch."""
        response = client.get("/api/search/profile?url=https://linkedin.com/in/johndoe")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John Doe"
        assert "experience" in data

    def test_profile_missing_url(self, client):
        """Test profile endpoint with missing URL parameter."""
        response = client.get("/api/search/profile")
        assert response.status_code == 422