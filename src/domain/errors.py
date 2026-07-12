class AppError(Exception):
    """Base for exceptions that carry a user-facing message and map to an error envelope.

    Shared by every error type that needs a `.message` an exception handler
    can read (see `core/errors.py`) - subclass this instead of `Exception`
    directly when adding a new error type.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    """Base exception for "entity not found" across domain resources."""
