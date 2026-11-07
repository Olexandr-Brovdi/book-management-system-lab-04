"""Custom domain collection using composition rather than inheriting list."""

from collections.abc import Iterator

from book_domain.models import Book
from book_domain.repositories import Repository


class BookCatalog:
    def __init__(self, repository: Repository[Book]) -> None:
        self._repository = repository

    def add(self, book: Book) -> None:
        self._repository.add(book)

    def get(self, book_id: int) -> Book | None:
        return self._repository.get(book_id)

    def __len__(self) -> int:
        return len(self._repository.all())

    def __iter__(self) -> Iterator[Book]:
        return iter(self._repository.all())

    def __getitem__(self, position: int) -> Book:
        return self._repository.all()[position]

    def __contains__(self, book_id: object) -> bool:
        if not isinstance(book_id, int) or isinstance(book_id, bool):
            return False
        return self.get(book_id) is not None

    def __str__(self) -> str:
        return f"Каталог: {len(self)} книг"
