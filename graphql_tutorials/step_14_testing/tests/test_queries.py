import pytest


def test_list_all_books(client):
    response = client.post("/graphql", json={
        "query": "{ books { id title author year } }"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["errors"] is None or "errors" not in data
    books = data["data"]["books"]
    assert len(books) == 3
    assert books[0]["title"] == "1984"


def test_get_book_by_id(client):
    response = client.post("/graphql", json={
        "query": '{ book(id: "1") { title author } }'
    })
    data = response.json()["data"]
    assert data["book"]["title"] == "1984"
    assert data["book"]["author"] == "George Orwell"


def test_get_book_not_found(client):
    response = client.post("/graphql", json={
        "query": '{ book(id: "999") { title } }'
    })
    data = response.json()["data"]
    assert data["book"] is None


@pytest.mark.parametrize("term,expected_count", [
    ("1984", 1),
    ("tolkien", 1),
    ("nonexistent", 0),
    ("the", 1),
])
def test_search(client, term, expected_count):
    response = client.post("/graphql", json={
        "query": f'{{ search(term: "{term}") {{ title }} }}'
    })
    data = response.json()["data"]
    assert len(data["search"]) == expected_count


def test_query_specific_fields(client):
    """Client should be able to request only specific fields."""
    response = client.post("/graphql", json={
        "query": "{ books { title } }"
    })
    data = response.json()["data"]
    book = data["books"][0]
    assert "title" in book
    assert "author" not in book
    assert "year" not in book


def test_query_with_variables(client):
    response = client.post("/graphql", json={
        "query": "query GetBook($id: ID!) { book(id: $id) { title } }",
        "variables": {"id": "2"},
    })
    data = response.json()["data"]
    assert data["book"]["title"] == "Dune"
