"""Seed the database: poetry run python -m app.seed"""

from .auth import hash_password
from .database import SessionLocal, create_tables
from .models import AuthorModel, BookModel, UserModel


def seed():
    create_tables()
    db = SessionLocal()

    if db.query(UserModel).count() > 0:
        print("Database already has data. Skipping seed.")
        db.close()
        return

    users = [
        UserModel(
            username="admin",
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
        ),
        UserModel(
            username="alice",
            email="alice@example.com",
            password_hash=hash_password("alice123"),
            role="user",
        ),
    ]
    db.add_all(users)
    db.commit()

    authors = [
        AuthorModel(name="George Orwell", bio="English novelist"),
        AuthorModel(name="Frank Herbert", bio="Sci-fi author"),
    ]
    db.add_all(authors)
    db.commit()

    books = [
        BookModel(title="1984", year=1949, genre="fiction", author_id=1),
        BookModel(title="Dune", year=1965, genre="science_fiction", author_id=2),
    ]
    db.add_all(books)
    db.commit()

    print(f"Seeded: {len(users)} users, {len(authors)} authors, {len(books)} books")
    print("Admin login: admin@example.com / admin123")
    print("User login:  alice@example.com / alice123")
    db.close()


if __name__ == "__main__":
    seed()
