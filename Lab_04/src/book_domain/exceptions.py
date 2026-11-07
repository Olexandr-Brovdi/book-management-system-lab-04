"""Small domain exception hierarchy."""


class LibraryError(Exception):
    """Base error of the book domain."""


class ValidationError(LibraryError, ValueError):
    """A value violates a domain invariant."""


class DuplicateIdError(LibraryError):
    """The repository already contains this identifier."""
