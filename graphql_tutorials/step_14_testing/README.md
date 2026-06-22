# Step 14: Testing GraphQL APIs

## Testing Approaches

### 1. Schema Tests (unit)
Test the schema directly without HTTP:
```python
result = await schema.execute("query { books { title } }")
assert result.errors is None
assert len(result.data["books"]) > 0
```

### 2. HTTP Tests (integration)
Test through the full HTTP stack using FastAPI's test client:
```python
response = client.post("/graphql", json={"query": "{ books { title } }"})
assert response.status_code == 200
```

### 3. Resolver Tests (unit)
Test individual resolvers in isolation.

---

## Running Tests

```bash
# From the project root (graphql_tutorials/)
poetry run pytest step_14_testing/tests -v
poetry run pytest step_14_testing/tests -v --tb=short    # Shorter output
poetry run pytest step_14_testing/tests/test_queries.py -v   # Run specific file
```

---

## What We Test

1. **Queries** - do they return correct data?
2. **Mutations** - do they create/update/delete correctly?
3. **Validation** - do invalid inputs get rejected?
4. **Error cases** - not found, bad input, etc.
5. **Auth** - protected fields require authentication

---

## Project Structure

```
step_14_testing/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_queries.py      # Query tests
│   └── test_mutations.py    # Mutation tests
└── pyproject.toml
```

---

## Key Patterns

### Fixtures (conftest.py)
Shared setup code that pytest automatically discovers:
```python
@pytest.fixture
def client():
    return TestClient(app)
```

### Parameterized Tests
Test multiple inputs with one test function:
```python
@pytest.mark.parametrize("title,expected_count", [
    ("1984", 1),
    ("nonexistent", 0),
])
def test_search(client, title, expected_count):
    ...
```

Next: [Step 15 - Rover CLI](../step_15_rover_cli/README.md)
