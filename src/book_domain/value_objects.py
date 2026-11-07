"""Immutable publication metadata with runtime invariants."""

from dataclasses import dataclass
from datetime import date

from book_domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class PublicationInfo:
    year: int
    publisher: str = "Невідоме видавництво"

    def __post_init__(self) -> None:
        if type(self.year) is not int or not 1 <= self.year <= date.today().year:
            raise ValidationError("Рік має бути цілим від 1 до поточного року")
        if not isinstance(self.publisher, str) or not self.publisher.strip():
            raise ValidationError("Видавництво не може бути порожнім")
        object.__setattr__(self, "publisher", self.publisher.strip())

    def __str__(self) -> str:
        return f"{self.year}, {self.publisher}"
