import logging
import os
import sqlite3
import unicodedata

from sqlalchemy import Engine, StaticPool, create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

logger = logging.getLogger(__name__)


IN_MEMORY_DB_URL = "sqlite:///:memory:"


class Base(DeclarativeBase):
    pass


def normalize(text: str) -> str:
    """
    Normalize text for better search results.

    >>> normalize("Český film")
    'cesky film'
    >>> normalize("Hrají: Jiřík, Štěpán")
    'hraji: jirik, stepan'
    """
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def create_disk_engine(db_file: str) -> Engine:
    """Write connection for Scrapper, data is saved to disk on each update."""
    db_url = f"sqlite:///{db_file}"
    return create_engine(db_url)


def create_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)


def create_memory_engine() -> Engine:
    """Read only connection for Web app, data is loaded from disk on app startup."""
    return create_engine(
        IN_MEMORY_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )


def create_scope_session(engine: Engine) -> scoped_session:
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)
    return scoped_session(session_factory)


def create_schema(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)


def load_from_disk(db_file_path: str, memory_engine: Engine) -> None:
    if not os.path.exists(db_file_path):
        logger.warning("Database file %s does not exist, creating empty database", db_file_path)
        create_schema(memory_engine)
        return

    source_connection = sqlite3.connect(f"file:{db_file_path}?mode=ro", uri=True)
    destination_connection = memory_engine.raw_connection().driver_connection

    source_connection.backup(destination_connection)

    source_connection.close()
