import os
import sys
import time
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import HTTPException
from app.utils import paths


class TestPathsSecurityAndCleanup(unittest.TestCase):
    def test_cleanup_deletes_only_files_older_than_max_age(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            old_file = Path(tmp_dir) / "old.pdf"
            new_file = Path(tmp_dir) / "new.pdf"
            old_file.write_text("old")
            new_file.write_text("new")

            now = time.time()
            os.utime(old_file, (now - 120, now - 120))
            os.utime(new_file, (now - 10, now - 10))

            original_tmp_dir = paths.TMP_DIR
            try:
                paths.TMP_DIR = Path(tmp_dir)
                deleted = paths.cleanup_tmp(max_age_seconds=60)
            finally:
                paths.TMP_DIR = original_tmp_dir

            self.assertEqual(deleted, 1)
            self.assertFalse(old_file.exists())
            self.assertTrue(new_file.exists())

    def test_cleanup_keeps_new_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            fresh_file = Path(tmp_dir) / "fresh.pdf"
            fresh_file.write_text("fresh")
            now = time.time()
            os.utime(fresh_file, (now - 5, now - 5))

            original_tmp_dir = paths.TMP_DIR
            try:
                paths.TMP_DIR = Path(tmp_dir)
                deleted = paths.cleanup_tmp(max_age_seconds=60)
            finally:
                paths.TMP_DIR = original_tmp_dir

            self.assertEqual(deleted, 0)
            self.assertTrue(fresh_file.exists())

    def test_validate_doc_id_blocks_path_traversal(self):
        with self.assertRaises(HTTPException) as ctx:
            paths.validate_doc_id("../etc/passwd")
        self.assertEqual(ctx.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
