import pytest
import sys
from pathlib import Path

# Add the apps/api directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "api"))


@pytest.fixture
def mock_db():
    """Mock database session for tests"""
    # In a real test, we'd use a test database
    pass


@pytest.fixture
def client():
    """Test client fixture"""
    from fastapi.testclient import TestClient
    from apps.api.main import app
    return TestClient(app)