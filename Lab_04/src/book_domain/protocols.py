"""Small structural interfaces, independent of concrete infrastructure."""

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from book_domain.dto import BookPayload


class HasId(Protocol):
    @property
    def id(self) -> int: ...


@runtime_checkable
class Exporter(Protocol):
    def export(self, records: Sequence[BookPayload]) -> str: ...
