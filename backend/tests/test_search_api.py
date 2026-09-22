import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestSearchEndpoint:
    """Tests for /api/search endpoint."""
    
    @patch("app.api.search.harvest_get")
    def test_search_alumni_success(self, mock_harvest):
        """Test successful alumni search."""
        mock_harvest.return_value = {
            "results": [
                {"name": "John Doe", "title": "Engineer", "url": "https://linkedin.com/in/johndoe"}
            ]
        }
        
        response = client.get("/api/search?query=John")
        
        assert response.status_code == 200
        assert "results" in response.json()
        mock_harvest.assert_called_once_with("/linkedin/lead-search", {"search": "John"})
    
    @patch("app.api.search.harvest_get")
    def test_search_alumni_empty_query(self, mock_harvest):
        """Test search with empty query returns 422."""
        response = client.get("/api/search?query=")
        
        assert response.status_code == 422
    
    @patch("app.api.search.harvest_get")
    def test_search_alumni_missing_query(self, mock_harvest):
        """Test search without query parameter returns 422."""
        response = client.get("/api/search")
        
        assert response.status_code == 422


class TestProfileEndpoint:
    """Tests for /api/search/profile endpoint."""
    
    @patch("app.api.search.harvest_get")
    def test_get_profile_success(self, mock_harvest):
        """Test successful profile fetch."""
        mock_harvest.return_value = {
            "name": "John Doe",
            "title": "Software Engineer",
            "company": "Tech Corp"
        }
        
        test_url = "https://linkedin.com/in/johndoe"
        response = client.get(f"/api/search/profile?url={test_url}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John Doe"
        mock_harvest.assert_called_once_with("/linkedin/profile", {"url": test_url})
    
    @patch("app.api.search.harvest_get")
    def test_get_profile_missing_url(self, mock_harvest):
        """Test profile fetch without URL returns 422."""
        response = client.get("/api/search/profile")
        
        assert response.status_code == 422


class TestHarvestIntegration:
    """Tests for Harvest API integration error handling."""
    
    @patch("app.integrations.harvest.get_secret")
    def test_harvest_missing_api_key(self, mock_secret):
        """Test that missing API key returns 500."""
        mock_secret.return_value = None
        
        response = client.get("/api/search?query=test")
        
        assert response.status_code == 500
        assert "HARVEST_API_KEY not configured" in response.json()["detail"]
    
    @patch("app.integrations.harvest.get_secret")
    @patch("app.integrations.harvest.httpx.Client")
    def test_harvest_connection_error(self, mock_client, mock_secret):
        """Test that connection error returns 502."""
        mock_secret.return_value = "test-api-key"
        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.get.side_effect = Exception("Connection refused")
        
        response = client.get("/api/search?query=test")
        
        assert response.status_code == 502
