import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.file_uploads import Upload

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@strawberry.type
class UploadResult:
    filename: str
    size: int
    content_type: str
    message: str


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Upload a file using the uploadCover mutation"


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def upload_cover(self, file: Upload) -> UploadResult:
        """Upload a book cover image.

        Accepts: .jpg, .jpeg, .png, .gif, .webp (max 5MB)
        """
        filename = file.filename or "unknown"

        ext = ""
        if "." in filename:
            ext = "." + filename.rsplit(".", 1)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File type '{ext}' not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        content = await file.read()
        size = len(content)

        if size > MAX_FILE_SIZE:
            raise ValueError(f"File too large ({size} bytes). Max: {MAX_FILE_SIZE}")

        return UploadResult(
            filename=filename,
            size=size,
            content_type=file.content_type or "application/octet-stream",
            message=f"Successfully uploaded '{filename}' ({size} bytes)",
        )

    @strawberry.mutation
    async def upload_multiple(self, files: list[Upload]) -> list[UploadResult]:
        """Upload multiple files at once."""
        results = []
        for file in files:
            content = await file.read()
            results.append(
                UploadResult(
                    filename=file.filename or "unknown",
                    size=len(content),
                    content_type=file.content_type or "application/octet-stream",
                    message=f"Uploaded '{file.filename}'",
                )
            )
        return results


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Book Review API - Step 13")
app.include_router(graphql_app, prefix="/graphql")
