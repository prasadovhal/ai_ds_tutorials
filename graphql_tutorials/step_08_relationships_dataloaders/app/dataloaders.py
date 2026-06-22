from collections import defaultdict

from strawberry.dataloader import DataLoader

from .database import SessionLocal
from .models import AuthorModel, BookModel, ReviewModel


async def load_authors(ids: list[int]) -> list[AuthorModel]:
    """Batch load authors by their IDs.

    DataLoader calls this ONCE with all requested IDs,
    instead of making N individual queries.
    """
    db = SessionLocal()
    try:
        authors = db.query(AuthorModel).filter(AuthorModel.id.in_(ids)).all()
        author_map = {a.id: a for a in authors}
        return [author_map.get(id) for id in ids]
    finally:
        db.close()


async def load_books_by_author(author_ids: list[int]) -> list[list[BookModel]]:
    """Batch load books grouped by author ID.

    For one-to-many relationships, we return a list of lists.
    Each inner list contains all books for one author.
    """
    db = SessionLocal()
    try:
        books = db.query(BookModel).filter(BookModel.author_id.in_(author_ids)).all()
        books_by_author: dict[int, list] = defaultdict(list)
        for book in books:
            books_by_author[book.author_id].append(book)
        return [books_by_author.get(aid, []) for aid in author_ids]
    finally:
        db.close()


async def load_reviews_by_book(book_ids: list[int]) -> list[list[ReviewModel]]:
    """Batch load reviews grouped by book ID."""
    db = SessionLocal()
    try:
        reviews = (
            db.query(ReviewModel).filter(ReviewModel.book_id.in_(book_ids)).all()
        )
        reviews_by_book: dict[int, list] = defaultdict(list)
        for review in reviews:
            reviews_by_book[review.book_id].append(review)
        return [reviews_by_book.get(bid, []) for bid in book_ids]
    finally:
        db.close()


class Loaders:
    """Container for all DataLoaders. Created fresh for each request."""

    def __init__(self):
        self.author_loader = DataLoader(load_fn=load_authors)
        self.books_by_author_loader = DataLoader(load_fn=load_books_by_author)
        self.reviews_by_book_loader = DataLoader(load_fn=load_reviews_by_book)
