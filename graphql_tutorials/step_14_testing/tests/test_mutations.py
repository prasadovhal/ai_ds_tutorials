def test_create_book(client):
    response = client.post("/graphql", json={
        "query": """
            mutation {
                createBook(input: {
                    title: "The Martian"
                    author: "Andy Weir"
                    year: 2011
                }) {
                    id
                    title
                    author
                    year
                }
            }
        """
    })
    data = response.json()["data"]
    book = data["createBook"]
    assert book["title"] == "The Martian"
    assert book["author"] == "Andy Weir"
    assert book["year"] == 2011
    assert book["id"] is not None


def test_create_book_empty_title_fails(client):
    response = client.post("/graphql", json={
        "query": """
            mutation {
                createBook(input: {
                    title: "  "
                    author: "Nobody"
                    year: 2025
                }) {
                    title
                }
            }
        """
    })
    data = response.json()
    assert data.get("errors") is not None
    assert "Title cannot be empty" in data["errors"][0]["message"]


def test_create_book_negative_year_fails(client):
    response = client.post("/graphql", json={
        "query": """
            mutation {
                createBook(input: {
                    title: "Bad Book"
                    author: "X"
                    year: -5
                }) {
                    title
                }
            }
        """
    })
    data = response.json()
    assert data.get("errors") is not None


def test_delete_book(client):
    response = client.post("/graphql", json={
        "query": """
            mutation {
                deleteBook(id: "1") {
                    success
                    message
                }
            }
        """
    })
    data = response.json()["data"]
    assert data["deleteBook"]["success"] is True

    # Verify it's gone
    response = client.post("/graphql", json={
        "query": '{ book(id: "1") { title } }'
    })
    assert response.json()["data"]["book"] is None


def test_delete_nonexistent_book(client):
    response = client.post("/graphql", json={
        "query": """
            mutation {
                deleteBook(id: "999") {
                    success
                    message
                }
            }
        """
    })
    data = response.json()["data"]
    assert data["deleteBook"]["success"] is False


def test_create_then_query(client):
    """Integration: create a book then find it by search."""
    client.post("/graphql", json={
        "query": """
            mutation {
                createBook(input: {
                    title: "Ender's Game"
                    author: "Orson Scott Card"
                    year: 1985
                }) { id }
            }
        """
    })

    response = client.post("/graphql", json={
        "query": '{ search(term: "Ender") { title author } }'
    })
    results = response.json()["data"]["search"]
    assert len(results) == 1
    assert results[0]["title"] == "Ender's Game"
