
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.baseline.baseline_manager import create_baseline
from app.hashing.file_hasher import calculate_sha256


class TestBaselineManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_directory = Path(self.temp_dir.name)

        self.db_path = self.test_directory / "fim_test.db"
        self.file_path = self.test_directory / "sample.txt"

        self.file_path.write_text("FIM trusted content")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_baseline(self):
        result = create_baseline(self.file_path, self.db_path)

        expected = calculate_sha256(self.file_path)

        self.assertEqual(result, expected)

    def test_baseline_is_stored_in_database(self):
        create_baseline(self.file_path, self.db_path)

        with sqlite3.connect(self.db_path) as connection:
            record = connection.execute(
                "SELECT file_path, hash_value FROM baselines"
            ).fetchone()

        self.assertIsNotNone(record)
        self.assertEqual(record[0], str(self.file_path.resolve()))
        self.assertEqual(record[1], calculate_sha256(self.file_path))

    def test_duplicate_baseline_is_rejected(self):
        create_baseline(self.file_path, self.db_path)

        with self.assertRaises(sqlite3.IntegrityError):
            create_baseline(self.file_path, self.db_path)

    def test_missing_file_is_rejected(self):
        missing_file = self.test_directory / "missing.txt"

        with self.assertRaises(FileNotFoundError):
            create_baseline(missing_file, self.db_path)


if __name__ == "__main__":
    unittest.main()
