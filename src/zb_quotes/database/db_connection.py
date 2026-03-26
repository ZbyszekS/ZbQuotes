import os
from dotenv import load_dotenv
from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import *
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()  # reads .env file

# Prefer DATABASE_URL from environment. If not provided, fall back to a local SQLite file path.
# You can override the default file path by setting LOCAL_SQLITE_PATH in your .env.
# DEFAULT_SQLITE_PATH = Path(
#     os.getenv(
#         "LOCAL_SQLITE_PATH",
#         "C:\\Users\\zbysz\\Documents\\moje-dokumenty-overt\\zawodowe\\programowanie\\databases\\SQLite\\portfolio_0_1_0\\port_0_1_0.sqlite3",
#     )
# )

# local_database_url = "sqlite:///C:\\Users\\zbysz\\Documents\\moje-dokumenty-overt\\zawodowe\\programowanie\\databases\\SQLite\\portfolio_0_1_0\\port_0_1_0.sqlite3"
# local_database_url = "sqlite:////mnt/WDB-500-ntfs/Users/zbysz/Moje dokumenty/moje-dokumenty-overt/zawodowe/programowanie/databases/SQLite/PORTFOLIO_0_1_0/port_0_1_0.sqlite3"
# ── Database connection ───────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL") # e.g., "sqlite:////path/to/your/database.db" defined in .env file
logger.info(f"Using DATABASE_URL: {DATABASE_URL}")
engine = create_engine(DATABASE_URL, echo=False)
# local_database_url = f"sqlite:///{SQLITE_DB_DIRECTORY}/{SQLITE_DB_FILENAME}"
# DATABASE_URL = os.getenv("DATABASE_URL", local_database_url) # left for reference, but not used
# DATABASE_URL = local_database_url

# ECHO_SQL     = os.getenv("SQLALCHEMY_ECHO", "false").lower() in {"1","true","yes"}

# engine = create_engine(DATABASE_URL, echo=ECHO_SQL)  # add echo=True for SQL logging
SessionClass = sessionmaker(bind=engine)  # configure autoflush/autocommit as needed

@contextmanager
def get_db_session():
    # Setup logic before yield
    session = SessionClass()
    try:
        yield session # The code inside the 'with' block runs here
        # Teardown logic for success (commit)
        session.commit()
    except Exception:
        # Teardown logic for failure (rollback)
        session.rollback()
        raise
    finally:
        # Teardown logic that always runs (close)
        session.close()
