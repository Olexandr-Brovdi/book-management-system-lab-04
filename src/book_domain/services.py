"""Application orchestration separated from entities and infrastructure."""

from dataclasses import dataclass

from book_domain.catalog import BookCatalog
from book_domain.dto import book_to_payload
from book_domain.models import Book
from book_domain.protocols import Exporter


class SearchService:
    def __init__(self, catalog: BookCatalog) -> None:
        self._catalog = catalog

    def by_author(self, name: str) -> tuple[Book, ...]:
        query = " ".join(name.split()).casefold()
        return tuple(
            book for book in self._catalog if book.author.name.casefold() == query
        )

    def by_title(self, title: str) -> tuple[Book, ...]:
        query = title.strip().casefold()
        if not query:
            return ()
        return tuple(book for book in self._catalog if query in book.title.casefold())

    def by_year(self, year: int) -> tuple[Book, ...]:
        return tuple(book for book in self._catalog if book.publication.year == year)


@dataclass(frozen=True, slots=True)
class CatalogReport:
    count: int
    average_pages: float
    largest_title: str | None


class ReportingService:
    def __init__(self, catalog: BookCatalog) -> None:
        self._catalog = catalog

    def largest_book(self) -> Book | None:
        return max(self._catalog, key=lambda book: book.pages, default=None)

    def build(self) -> CatalogReport:
        count = len(self._catalog)
        largest = self.largest_book()
        average = sum(book.pages for book in self._catalog) / count if count else 0.0
        return CatalogReport(count, average, largest.title if largest else None)


class ExportService:
    def __init__(self, catalog: BookCatalog, exporter: Exporter) -> None:
        self._catalog = catalog
        self._exporter = exporter

    def render(self) -> str:
        return self._exporter.export(
            tuple(book_to_payload(book) for book in self._catalog)
        )


class LibraryRegistry:
    """A library has a catalogue, search/reporting and an injected export service."""

    def __init__(self, name: str, catalog: BookCatalog, exporter: Exporter) -> None:
        self.name = name
        self.catalog = catalog
        self.search = SearchService(catalog)
        self.reporting = ReportingService(catalog)
        self.exporting = ExportService(catalog, exporter)

    def register(self, book: Book) -> None:
        self.catalog.add(book)

    def export(self) -> str:
        return self.exporting.render()
