import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestSearchEndpoint:
    @patch("app.api.search.harvest_get")
    def test_search_alumni_success(self, mock_harvest):
        """Test successful alumni search."""
        mock_harvest.return_value = {
            "items": [
                {
                    "name": "John Doe",
                    "title": "Engineer",
                    "company": "Tech Corp",
                    "url": "https://linkedin.com/in/johndoe"
                }
            ]
        }
        
        response = client.get("/api/search?query=john")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "John Doe"
        assert data[0]["title"] == "Engineer"
        mock_harvest.assert_called_once_with("/linkedin/lead-search", {"search": "john"})

    @patch("app.api.search.harvest_get")
    def test_search_alumni_empty_results(self, mock_harvest):
        """Test search with no results."""
        mock_harvest.return_value = {"items": []}
        
        response = client.get("/api/search?query=nonexistent")
        
        assert response.status_code == 200
        assert response.json() == []

    def test_search_alumni_missing_query(self):
        """Test search without query parameter."""
        response = client.get("/api/search")
        assert response.status_code == 422


class TestProfileEndpoint:
    @patch("app.api.search.harvest_get")
    def test_get_profile_success(self, mock_harvest):
        """Test successful profile fetch."""
        mock_harvest.return_value = {
            "name": "Jane Smith",
            "title": "Manager",
            "company": "Business Inc",
            "location": "New York",
            "summary": "Experienced professional",
            "url": "https://linkedin.com/in/janesmith"
        }
        
        response = client.get("/api/profile?url=https://linkedin.com/in/janesmith")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Smith"
        assert data["title"] == "Manager"
        mock_harvest.assert_called_once_with(
            "/linkedin/profile",
            {"url": "https://linkedin.com/in/janesmith"}
        )

    def test_get_profile_missing_url(self):
        """Test profile fetch without URL parameter."""
        response = client.get("/api/profile")
        assert response.status_code == 422


class TestHarvestIntegration:
    @patch("app.api.search.get_secret")
    def test_harvest_get_missing_key(self, mock_get_secret):
        """Test that missing API key returns proper error."""
        mock_get_secret.return_value = None
        
        response = client.get("/api/search?query=test")
        
        assert response.status_code == 500
        assert "HARVEST_API_KEY not configured" in response.json()["detail"]
