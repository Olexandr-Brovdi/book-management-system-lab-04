"""Domain invariants, substitution, generic repository and injected adapters."""

import csv
import io
import json
import unittest
from dataclasses import FrozenInstanceError

from book_domain.catalog import BookCatalog
from book_domain.design_experiments import (
    ComposedTitleProcessor,
    DelimitedParser,
    DelimitedTitleProcessor,
    FakeExporter,
    JoinedFormatter,
    NonEmptyValidator,
)
from book_domain.dto import book_from_payload, book_to_payload
from book_domain.exceptions import DuplicateIdError, ValidationError
from book_domain.exporters import CsvExporter, JsonExporter
from book_domain.main import create_demo_registry
from book_domain.models import Author, Book, EBook
from book_domain.protocols import Exporter
from book_domain.repositories import InMemoryRepository, Repository
from book_domain.services import ExportService, ReportingService, SearchService
from book_domain.value_objects import PublicationInfo


class DomainTests(unittest.TestCase):
    def setUp(self):
        self.registry = create_demo_registry()

    def test_all_variant_operations(self):
        self.assertEqual(len(self.registry.catalog), 4)
        self.assertEqual(len(self.registry.search.by_author(" ІВАН ФРАНКО ")), 2)
        self.assertEqual(self.registry.search.by_title("кобзар")[0].id, 1)
        self.assertEqual(self.registry.search.by_year(1911)[0].title, "Лісова пісня")
        self.assertEqual(self.registry.reporting.largest_book().title, "Кобзар")
        self.assertEqual(self.registry.reporting.build().average_pages, 168.0)

    def test_property_rejects_invalid_update(self):
        book = self.registry.catalog[0]
        with self.assertRaises(ValidationError):
            book.pages = -1
        self.assertEqual(book.pages, 240)
        book.pages = 250
        self.assertEqual(book.pages, 250)

    def test_runtime_validation(self):
        for value in (0, -1, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                Book(10, "A", Author(1, "B"), PublicationInfo(2000), value)
        with self.assertRaises(ValidationError):
            Author(1, " ")
        with self.assertRaises(ValidationError):
            PublicationInfo(0)
        with self.assertRaises(ValidationError):
            Book(1, " ", Author(1, "A"), PublicationInfo(2000), 10)

    def test_frozen_value_object(self):
        publication = PublicationInfo(2000)
        with self.assertRaises(FrozenInstanceError):
            publication.year = 2001

    def test_substitution(self):
        electronic = EBook(
            5, "Цифрова книга", Author(1, "Автор"), PublicationInfo(2020), 300
        )
        self.registry.register(electronic)
        self.assertIs(self.registry.reporting.largest_book(), electronic)
        self.assertIn("epub", str(electronic))
        self.assertIsInstance(electronic, Book)

    def test_duplicate_preserves_existing(self):
        original = self.registry.catalog[0]
        with self.assertRaises(DuplicateIdError):
            self.registry.register(original)
        self.assertEqual(len(self.registry.catalog), 4)

    def test_custom_collection(self):
        self.assertTrue(1 in self.registry.catalog)
        self.assertFalse(True in self.registry.catalog)
        self.assertFalse("1" in self.registry.catalog)
        self.assertEqual(len(list(self.registry.catalog)), 4)
        self.assertEqual(self.registry.catalog[-1].id, 4)
        with self.assertRaises(IndexError):
            self.registry.catalog[100]
        self.assertIn("Book(", repr(self.registry.catalog[0]))

    def test_empty_catalogue(self):
        catalog = BookCatalog(InMemoryRepository[Book]())
        self.assertIsNone(catalog.get(1))
        self.assertIsNone(ReportingService(catalog).largest_book())
        self.assertEqual(ReportingService(catalog).build().average_pages, 0.0)
        self.assertEqual(SearchService(catalog).by_title(""), ())

    def test_injected_fake_without_inheritance(self):
        fake = FakeExporter()
        self.assertIsInstance(fake, Exporter)
        service = ExportService(self.registry.catalog, fake)
        self.assertEqual(service.render(), "FAKE:4")
        self.assertEqual(fake.calls, 1)

    def test_export_strategies(self):
        records = tuple(book_to_payload(book) for book in self.registry.catalog)
        self.assertEqual(len(json.loads(JsonExporter().export(records))), 4)
        rows = list(csv.reader(io.StringIO(CsvExporter().export(records))))
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[1][1], "Кобзар")

    def test_typed_payload_roundtrip(self):
        electronic = self.registry.catalog[2]
        restored = book_from_payload(book_to_payload(electronic))
        self.assertIsInstance(restored, EBook)
        self.assertEqual(book_to_payload(restored), book_to_payload(electronic))

    def test_generic_author_repository(self):
        repo = InMemoryRepository[Author]()
        author = Author(1, "Автор")
        repo.add(author)
        self.assertIs(repo.get(1), author)

    def test_abstract_base(self):
        with self.assertRaises(TypeError):
            Repository()

    def test_design_equivalence(self):
        composed = ComposedTitleProcessor(
            DelimitedParser(), NonEmptyValidator(), JoinedFormatter()
        )
        inherited = DelimitedTitleProcessor()
        self.assertEqual(composed.process(" A ; B "), inherited.process(" A ; B "))
        for processor in (composed, inherited):
            with self.assertRaises(ValueError):
                processor.process("A;;B")
