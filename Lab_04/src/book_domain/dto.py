"""Typed external mappings and an explicit class factory boundary."""

from typing import NotRequired, TypedDict

from book_domain.models import Author, Book, EBook
from book_domain.value_objects import PublicationInfo


class BookPayload(TypedDict):
    id: int
    title: str
    author_id: int
    author_name: str
    year: int
    pages: int
    publisher: str
    file_format: NotRequired[str]


def book_from_payload(data: BookPayload) -> Book:
    author = Author(data["author_id"], data["author_name"])
    publication = PublicationInfo(data["year"], data["publisher"])
    if "file_format" in data:
        return EBook(
            data["id"],
            data["title"],
            author,
            publication,
            data["pages"],
            data["file_format"],
        )
    return Book(data["id"], data["title"], author, publication, data["pages"])


def book_to_payload(book: Book) -> BookPayload:
    result: BookPayload = {
        "id": book.id,
        "title": book.title,
        "author_id": book.author.id,
        "author_name": book.author.name,
        "year": book.publication.year,
        "pages": book.pages,
        "publisher": book.publication.publisher,
    }
    if isinstance(book, EBook):
        result["file_format"] = book.file_format
    return result
