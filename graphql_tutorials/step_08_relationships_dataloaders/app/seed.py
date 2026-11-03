"""Seed the database: poetry run python -m app.seed"""

from .database import SessionLocal, create_tables
from .models import AuthorModel, BookModel, ReviewModel


def seed():
    create_tables()
    db = SessionLocal()

    if db.query(AuthorModel).count() > 0:
        print("Database already has data. Skipping seed.")
        db.close()
        return

    authors = [
        AuthorModel(name="George Orwell", bio="English novelist and essayist"),
        AuthorModel(name="Frank Herbert", bio="American science fiction author"),
        AuthorModel(name="J.R.R. Tolkien", bio="English writer and philologist"),
        AuthorModel(name="Agatha Christie", bio="English writer known for detective novels"),
    ]
    db.add_all(authors)
    db.commit()

    books = [
        BookModel(title="1984", year=1949, genre="fiction", author_id=1),
        BookModel(title="Animal Farm", year=1945, genre="fiction", author_id=1),
        BookModel(title="Dune", year=1965, genre="science_fiction", author_id=2),
        BookModel(title="The Hobbit", year=1937, genre="fantasy", author_id=3),
        BookModel(title="The Lord of the Rings", year=1954, genre="fantasy", author_id=3),
        BookModel(title="Murder on the Orient Express", year=1934, genre="mystery", author_id=4),
    ]
    db.add_all(books)
    db.commit()

    reviews = [
        ReviewModel(rating=5, comment="A masterpiece of dystopian fiction", book_id=1),
        ReviewModel(rating=4, comment="Still relevant today", book_id=1),
        ReviewModel(rating=5, comment="The greatest sci-fi novel ever", book_id=3),
        ReviewModel(rating=5, comment="A perfect adventure story", book_id=4),
        ReviewModel(rating=4, comment="Epic world-building", book_id=5),
    ]
    db.add_all(reviews)
    db.commit()

    print(f"Seeded: {len(authors)} authors, {len(books)} books, {len(reviews)} reviews")
    db.close()


if __name__ == "__main__":
    seed()
