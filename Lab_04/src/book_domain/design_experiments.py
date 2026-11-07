"""Executable design comparisons: fixed dependency versus DI and two processors."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Protocol

from book_domain.catalog import BookCatalog
from book_domain.dto import BookPayload, book_to_payload
from book_domain.exporters import JsonExporter
from book_domain.services import ExportService


class HardwiredExportService:
    """Variant A: replacing the exporter requires modifying or patching this class."""

    def __init__(self, catalog: BookCatalog) -> None:
        self._catalog = catalog
        self._exporter = JsonExporter()

    def render(self) -> str:
        return self._exporter.export(tuple(book_to_payload(b) for b in self._catalog))


class FakeExporter:
    def __init__(self) -> None:
        self.calls = 0

    def export(self, records: Sequence[BookPayload]) -> str:
        self.calls += 1
        return f"FAKE:{len(records)}"


class BaseTitleProcessor(ABC):
    """Inheritance design: algorithm fixed in base, parsing is its extension point."""

    def process(self, text: str) -> str:
        values = self.parse(text)
        if not values or any(not value for value in values):
            raise ValueError("Порожня назва")
        return " | ".join(values)

    @abstractmethod
    def parse(self, text: str) -> tuple[str, ...]: ...


class DelimitedTitleProcessor(BaseTitleProcessor):
    def parse(self, text: str) -> tuple[str, ...]:
        return tuple(part.strip() for part in text.split(";"))


class TitleParser(Protocol):
    def parse(self, text: str) -> tuple[str, ...]: ...


class TitleValidator(Protocol):
    def validate(self, values: tuple[str, ...]) -> None: ...


class TitleFormatter(Protocol):
    def format(self, values: tuple[str, ...]) -> str: ...


class DelimitedParser:
    def parse(self, text: str) -> tuple[str, ...]:
        return tuple(part.strip() for part in text.split(";"))


class NonEmptyValidator:
    def validate(self, values: tuple[str, ...]) -> None:
        if not values or any(not value for value in values):
            raise ValueError("Порожня назва")


class JoinedFormatter:
    def format(self, values: tuple[str, ...]) -> str:
        return " | ".join(values)


class ComposedTitleProcessor:
    """Composition design: parser, validator and formatter vary independently."""

    def __init__(
        self, parser: TitleParser, validator: TitleValidator, formatter: TitleFormatter
    ) -> None:
        self._parser = parser
        self._validator = validator
        self._formatter = formatter

    def process(self, text: str) -> str:
        values = self._parser.parse(text)
        self._validator.validate(values)
        return self._formatter.format(values)


def run_design_experiments(catalog: BookCatalog) -> dict[str, str]:
    fixed = HardwiredExportService(catalog)
    fake = FakeExporter()
    injected = ExportService(catalog, fake)
    text = "Кобзар; Мойсей"
    inherited = DelimitedTitleProcessor().process(text)
    composed = ComposedTitleProcessor(
        DelimitedParser(), NonEmptyValidator(), JoinedFormatter()
    ).process(text)
    assert inherited == composed
    return {
        "hardwired": fixed.render()[:1],
        "injected": injected.render(),
        "inheritance": inherited,
        "composition": composed,
        "fake_calls": str(fake.calls),
    }
