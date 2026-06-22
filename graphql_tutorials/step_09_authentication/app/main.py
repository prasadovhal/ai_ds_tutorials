from contextlib import asynccontextmanager

import strawberry
from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter

from .auth import decode_token
from .database import SessionLocal, create_tables
from .models import UserModel
from .schema import Mutation, Query


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


async def get_context(request: Request):
    db = SessionLocal()
    user = None

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        payload = decode_token(token)
        if payload:
            user = db.query(UserModel).get(int(payload["sub"]))

    try:
        yield {"db": db, "user": user, "request": request}
    finally:
        db.close()


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI(title="Book Review API - Step 09", lifespan=lifespan)
app.include_router(graphql_app, prefix="/graphql")
