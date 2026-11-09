
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from app.hashing.file_hasher import calculate_sha256


def initialize_baseline_store(db_path: str | Path) -> None:
    """
    Create the SQLite database and baseline table
    if they do not already exist.
    """

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL UNIQUE,
                hash_value TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                modified_at TEXT NOT NULL,
                baseline_version INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)

        connection.commit()

    finally:
        connection.close()


def create_baseline(
    file_path: str | Path,
    db_path: str | Path
) -> str:
    """
    Create a trusted SHA-256 baseline for a file.

    Returns:
        The SHA-256 hash of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        sqlite3.IntegrityError: If a baseline already exists.
    """

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    canonical_path = str(file_path.resolve())

    # Calculate the file's SHA-256 hash.
    file_hash = calculate_sha256(file_path)

    # Collect file metadata.
    file_stats = file_path.stat()

    size_bytes = file_stats.st_size

    modified_at = datetime.fromtimestamp(
        file_stats.st_mtime,
        timezone.utc
    ).isoformat()

    initialize_baseline_store(db_path)

    connection = sqlite3.connect(db_path)

    try:
        connection.execute(
            """
            INSERT INTO baselines (
                file_path,
                hash_value,
                size_bytes,
                modified_at,
                baseline_version,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                canonical_path,
                file_hash,
                size_bytes,
                modified_at,
                1,
                datetime.now(timezone.utc).isoformat()
            )
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return file_hash
