import pytest
import tempfile
import os
from pathlib import Path
from app.services.data_manager import DataManager


@pytest.fixture
def temp_data_file():
    """Create a temporary data file for testing."""
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def data_manager(temp_data_file):
    """Create a DataManager instance with temporary file."""
    return DataManager(temp_data_file)


@pytest.fixture
def sample_data():
    """Sample data for testing."""
    return {
        "area1": [
            {"id": 1, "name": "service1", "type": "web", "url": "http://example.com", "version": "1.0", "status": "active"},
            {"id": 2, "name": "service2", "type": "api", "url": "http://api.example.com", "version": "2.0", "status": "inactive"}
        ],
        "area2": [
            {"id": 1, "name": "service3", "type": "db", "url": "http://db.example.com", "version": "1.5", "status": "active"}
        ]
    }
