"""Nominal repository abstraction and parameterized in-memory implementation."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from book_domain.exceptions import DuplicateIdError
from book_domain.protocols import HasId

T = TypeVar("T", bound=HasId)


class Repository(ABC, Generic[T]):
    @abstractmethod
    def add(self, item: T) -> None: ...

    @abstractmethod
    def get(self, item_id: int) -> T | None: ...

    @abstractmethod
    def all(self) -> tuple[T, ...]: ...


class InMemoryRepository(Repository[T]):
    def __init__(self) -> None:
        self._items: dict[int, T] = {}

    def add(self, item: T) -> None:
        if item.id in self._items:
            raise DuplicateIdError(f"ID {item.id} уже існує")
        self._items[item.id] = item

    def get(self, item_id: int) -> T | None:
        return self._items.get(item_id)

    def all(self) -> tuple[T, ...]:
        return tuple(self._items.values())
