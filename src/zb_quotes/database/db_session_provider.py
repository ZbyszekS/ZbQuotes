from contextlib import AbstractContextManager
from zb_quotes.database.db_connection import SessionClass

class DBSessionProvider_version1(AbstractContextManager):
    """Reusable, type-hinted session provider"""


    def __enter__(self) -> SessionClass:
        self._session = SessionClass()
        return self._session
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            self._session.commit()
        else:
            self._session.rollback()

        self._session.close()
        return False  # Don't suppress exceptions
    
    # Can add helper methods
    def is_active(self) -> bool:
        return self._session is not None


# Usage is identical to @contextmanager version
# with DBSessionProvider() as session:
#     session.query(...)


class DBSessionProvider(AbstractContextManager):
    """Reusable, type-hinted session provider with automatic commit/rollback."""

    def __init__(self) -> None:
        self._session: SessionClass | None = None

    def __enter__(self) -> SessionClass:
        self._session = SessionClass()  # or SessionClass(bind=engine) etc.
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._session is None:
            return False

        try:
            if exc_type is None:
                self._session.commit()
            else:
                self._session.rollback()
        finally:
            # Always close, even if commit/rollback fails
            self._session.close()
            self._session = None  # Clean up reference

        return False  # Do not suppress the exception

    def is_active(self) -> bool:
        """Check if a session is currently active within this provider."""
        return self._session is not None