
import hashlib
import tempfile
import unittest
from pathlib import Path

from app.hashing.file_hasher import calculate_sha256


class TestFileHasher(unittest.TestCase):

    def test_hash_calculation(self):
        content = b"FIM 2.0 security project"

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.txt"
            file_path.write_bytes(content)

            expected_hash = hashlib.sha256(content).hexdigest()
            actual_hash = calculate_sha256(file_path)

            self.assertEqual(actual_hash, expected_hash)

    def test_hash_changes_when_file_changes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.txt"

            file_path.write_text("Original content")
            original_hash = calculate_sha256(file_path)

            file_path.write_text("Modified content")
            modified_hash = calculate_sha256(file_path)

            self.assertNotEqual(original_hash, modified_hash)


if __name__ == "__main__":
    unittest.main()
