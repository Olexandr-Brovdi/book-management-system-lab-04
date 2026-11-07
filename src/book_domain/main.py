"""Composition root and demonstration of all operations of variant 2."""

import argparse
from dataclasses import asdict
from pathlib import Path

from book_domain.catalog import BookCatalog
from book_domain.design_experiments import run_design_experiments
from book_domain.dto import BookPayload, book_from_payload
from book_domain.exporters import CsvExporter, JsonExporter
from book_domain.models import Author, Book, EBook
from book_domain.protocols import Exporter
from book_domain.repositories import InMemoryRepository
from book_domain.services import LibraryRegistry
from book_domain.value_objects import PublicationInfo


def create_demo_registry(exporter: Exporter | None = None) -> LibraryRegistry:
    catalog = BookCatalog(InMemoryRepository[Book]())
    registry = LibraryRegistry(
        "Навчальна бібліотека",
        catalog,
        exporter if exporter is not None else JsonExporter(),
    )
    franko = Author(2, "Іван Франко")
    registry.register(
        Book(1, "Кобзар", Author(1, "Тарас Шевченко"), PublicationInfo(1840), 240)
    )
    registry.register(Book(2, "Захар Беркут", franko, PublicationInfo(1883), 192))
    registry.register(EBook(3, "Мойсей", franko, PublicationInfo(1905), 80, "epub"))
    payload: BookPayload = {
        "id": 4,
        "title": "Лісова пісня",
        "author_id": 3,
        "author_name": "Леся Українка",
        "year": 1911,
        "pages": 160,
        "publisher": "Навчальне видання",
    }
    registry.register(book_from_payload(payload))
    return registry


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lab_04 Варіант 2 — система обліку книг"
    )
    parser.add_argument("--export", type=Path)
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    args = parser.parse_args()
    exporter: Exporter = JsonExporter() if args.format == "json" else CsvExporter()
    registry = create_demo_registry(exporter)
    print("КАТАЛОГ:", registry.catalog)
    for book in registry.catalog:
        print(book)
    print(
        "АВТОР ІВАН ФРАНКО:",
        [b.title for b in registry.search.by_author("іван франко")],
    )
    print("НАЗВА КОБЗАР:", [b.title for b in registry.search.by_title("кобзар")])
    print("РІК 1911:", [b.title for b in registry.search.by_year(1911)])
    print("ЗВІТ:", asdict(registry.reporting.build()))
    print(
        "DUnder len/contains/getitem:",
        len(registry.catalog),
        1 in registry.catalog,
        registry.catalog[0].title,
    )
    print("PROTOCOL:", isinstance(exporter, Exporter))
    print("DESIGN EXPERIMENTS:", run_design_experiments(registry.catalog))
    if args.export:
        args.export.parent.mkdir(parents=True, exist_ok=True)
        args.export.write_text(registry.export(), encoding="utf-8")
        print("EXPORTED:", args.export)


if __name__ == "__main__":
    main()
