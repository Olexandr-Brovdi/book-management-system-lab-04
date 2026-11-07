"""Domain entities: authors, books, and a substitutable electronic-book subtype."""

from dataclasses import dataclass
from typing import ClassVar

from book_domain.exceptions import ValidationError
from book_domain.value_objects import PublicationInfo


@dataclass(frozen=True, slots=True)
class Author:
    id: int
    name: str

    def __post_init__(self) -> None:
        if type(self.id) is not int or self.id < 1:
            raise ValidationError("ID автора має бути додатним цілим")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValidationError("Ім'я автора не може бути порожнім")
        object.__setattr__(self, "name", " ".join(self.name.split()))


class Book:
    kind: ClassVar[str] = "book"

    def __init__(
        self,
        book_id: int,
        title: str,
        author: Author,
        publication: PublicationInfo,
        pages: int,
    ) -> None:
        if type(book_id) is not int or book_id < 1:
            raise ValidationError("ID книги має бути додатним цілим")
        if not isinstance(title, str) or not title.strip():
            raise ValidationError("Назва книги не може бути порожньою")
        self._id = book_id
        self._title = " ".join(title.split())
        self._author = author
        self._publication = publication
        self.pages = pages

    @property
    def id(self) -> int:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def author(self) -> Author:
        return self._author

    @property
    def publication(self) -> PublicationInfo:
        return self._publication

    @property
    def pages(self) -> int:
        return self._pages

    @pages.setter
    def pages(self, value: int) -> None:
        if type(value) is not int or value < 1:
            raise ValidationError("Кількість сторінок має бути додатним цілим")
        self._pages = value

    def __str__(self) -> str:
        return f"{self.title} | {self.author.name} | {self.publication.year} | {self.pages} стор."

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id!r}, title={self.title!r}, pages={self.pages!r})"


class EBook(Book):
    kind: ClassVar[str] = "ebook"

    def __init__(
        self,
        book_id: int,
        title: str,
        author: Author,
        publication: PublicationInfo,
        pages: int,
        file_format: str = "epub",
    ) -> None:
        super().__init__(book_id, title, author, publication, pages)
        normalized = file_format.strip().casefold()
        if normalized not in {"epub", "pdf"}:
            raise ValidationError("Формат електронної книги: epub або pdf")
        self._file_format = normalized

    @property
    def file_format(self) -> str:
        return self._file_format

    def __str__(self) -> str:
        return f"{super().__str__()} | {self.file_format}"
