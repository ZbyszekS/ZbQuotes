from contextlib import AbstractContextManager
from zb_portfolio_api.database.db_connection import SessionClass

class DBSessionProvider(AbstractContextManager):
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