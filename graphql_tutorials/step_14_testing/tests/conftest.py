import pytest
from fastapi.testclient import TestClient

from step_14_testing.app.main import BOOKS, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_books():
    """Reset the in-memory database before each test."""
    original = [
        {"id": "1", "title": "1984", "author": "George Orwell", "year": 1949},
        {"id": "2", "title": "Dune", "author": "Frank Herbert", "year": 1965},
        {"id": "3", "title": "The Hobbit", "author": "J.R.R. Tolkien", "year": 1937},
    ]
    BOOKS.clear()
    BOOKS.extend(original)
    yield
    BOOKS.clear()
    BOOKS.extend(original)
