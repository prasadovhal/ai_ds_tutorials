from contextlib import asynccontextmanager

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from .database import SessionLocal, create_tables
from .schema import Mutation, Query


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


async def get_context():
    db = SessionLocal()
    try:
        yield {"db": db}
    finally:
        db.close()


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI(title="Book Review API - Step 07", lifespan=lifespan)
app.include_router(graphql_app, prefix="/graphql")
