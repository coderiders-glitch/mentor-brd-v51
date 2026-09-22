import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def mock_harvest_api():
    """Mock Harvest API responses."""
    mock_search_results = [
        {"name": "John Doe", "title": "Software Engineer", "linkedin_url": "https://linkedin.com/in/johndoe"},
        {"name": "Jane Smith", "title": "Product Manager", "linkedin_url": "https://linkedin.com/in/janesmith"},
    ]
    mock_profile = {
        "name": "John Doe",
        "headline": "Senior Software Engineer at Tech Corp",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "experience": [
            {"role": "Senior Engineer", "company": "Tech Corp", "duration": "2020-Present"},
            {"role": "Software Engineer", "company": "Startup Inc", "duration": "2018-2020"},
        ]
    }
    return {"search": mock_search_results, "profile": mock_profile}


@pytest.fixture
def mock_get_secret(mock_harvest_api):
    """Mock get_secret to return a fake API key."""
    with patch("app.secretsmanager.get_secret") as mock:
        mock.return_value = "test-api-key"
        yield mock


@pytest.fixture
def mock_harvest_client(mock_harvest_api, mock_get_secret):
    """Mock Harvest API client functions."""
    with patch("app.services.harvest_client.search_linkedin_leads") as mock_search, \
         patch("app.services.harvest_client.get_linkedin_profile") as mock_profile:
        mock_search.return_value = mock_harvest_api["search"]
        mock_profile.return_value = mock_harvest_api["profile"]
        yield {"search": mock_search, "profile": mock_profile}


@pytest.fixture
def client(mock_harvest_client):
    """Create a test client with mocked dependencies."""
    from app.main import app
    return TestClient(app)