# Step 13: File Uploads

## GraphQL and Files

GraphQL doesn't natively handle file uploads. The community standard is the
**GraphQL Multipart Request Specification**, which Strawberry supports.

---

## How It Works

```
Client sends multipart/form-data:
  - operations: { "query": "mutation($file: Upload!) { ... }", "variables": { "file": null } }
  - map: { "0": ["variables.file"] }
  - 0: <actual file bytes>
```

Strawberry handles all the multipart parsing - you just use the `Upload` scalar.

---

## Running This Step

```bash
# From the project root (graphql_tutorials/)
poetry run uvicorn step_13_file_uploads.app.main:app --reload
```

### Upload via curl:
```bash
curl http://localhost:8000/graphql \
  -F operations='{"query":"mutation($file: Upload!) { uploadCover(file: $file) { filename size } }","variables":{"file":null}}' \
  -F map='{"0":["variables.file"]}' \
  -F 0=@/path/to/image.jpg
```

### Upload via Python:
```python
import httpx

with open("cover.jpg", "rb") as f:
    response = httpx.post(
        "http://localhost:8000/graphql",
        data={
            "operations": '{"query":"mutation($file: Upload!) { uploadCover(file: $file) { filename size } }","variables":{"file":null}}',
            "map": '{"0":["variables.file"]}',
        },
        files={"0": ("cover.jpg", f, "image/jpeg")},
    )
    print(response.json())
```

---

## Best Practices

1. **Validate file types** - check MIME type and extension
2. **Limit file size** - prevent abuse
3. **Store externally** - use S3/GCS in production, not local disk
4. **Return metadata** - filename, size, URL after upload

Next: [Step 14 - Testing](../step_14_testing/README.md)
