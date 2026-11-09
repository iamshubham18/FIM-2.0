
import hashlib
from pathlib import Path


def calculate_sha256(file_path: str | Path) -> str:
    """
    Calculate the SHA-256 hash of a file.

    Reads the file in chunks to support large files
    without loading the entire file into memory.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            sha256.update(chunk)

    return sha256.hexdigest()
