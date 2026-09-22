import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_harvest_search():
    with patch("app.services.harvest_client.search_linkedin_leads") as mock:
        yield mock


@pytest.fixture
def mock_harvest_profile():
    with patch("app.services.harvest_client.get_linkedin_profile") as mock:
        yield mock