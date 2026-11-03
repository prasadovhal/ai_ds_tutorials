from sqlalchemy import Column, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class AuthorModel(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    bio = Column(Text, nullable=True)

    books = relationship("BookModel", back_populates="author")


class BookModel(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(300), nullable=False)
    year = Column(Integer, nullable=False)
    genre = Column(String(50), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)

    author = relationship("AuthorModel", back_populates="books")
    reviews = relationship("ReviewModel", back_populates="book")


class ReviewModel(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    book = relationship("BookModel", back_populates="reviews")
