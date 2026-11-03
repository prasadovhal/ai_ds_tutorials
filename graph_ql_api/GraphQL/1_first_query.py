import os
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
import strawberry
from strawberry.fastapi import GraphQLRouter

# =========================
# 1. DATABASE SETUP
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 👉 Change filename here if needed
DB_FILE = "chinbook.sqlite"   # or "Chinook.db"

DB_PATH = os.path.join(BASE_DIR, DB_FILE)

print("📁 BASE DIR:", BASE_DIR)
print("📄 DB PATH:", DB_PATH)
print("✅ DB EXISTS:", os.path.exists(DB_PATH))

engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# =========================
# 2. DEBUG: CHECK TABLES
# =========================

inspector = inspect(engine)
print("📊 TABLES:", inspector.get_table_names())

# =========================
# 3. SQLAlchemy MODEL
# =========================

class ArtistModel(Base):
    __tablename__ = "Artist"
    ArtistId = Column(Integer, primary_key=True)
    Name = Column(String)

# =========================
# 4. GRAPHQL TYPES
# =========================

@strawberry.type
class Artist:
    artistId: int
    name: str

# =========================
# 5. QUERY RESOLVER
# =========================

@strawberry.type
class Query:

    @strawberry.field
    def artists(self) -> list[Artist]:
        db = SessionLocal()
        artists = db.query(ArtistModel).all()

        return [
            Artist(
                artistId=a.ArtistId,
                name=a.Name
            )
            for a in artists
        ]

# =========================
# 6. GRAPHQL APP
# =========================

schema = strawberry.Schema(query=Query)

app = FastAPI()

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# Optional root route
@app.get("/")
def root():
    return {"message": "Go to /graphql to use GraphQL UI"}
