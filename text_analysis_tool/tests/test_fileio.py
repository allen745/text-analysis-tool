"""Tests for text_analyzer.fileio (uses real temporary files)."""

import os
import tempfile
import unittest

from text_analyzer.fileio import (
    TextFileError,
    clean_path,
    read_text_file,
    save_report,
)


class TestReadTextFile(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)

    def _write(self, name, data, mode="w", **kwargs):
        path = os.path.join(self.folder.name, name)
        with open(path, mode, **kwargs) as handle:
            handle.write(data)
        return path

    def test_reads_a_normal_file(self):
        path = self._write("a.txt", "Python is easy.", encoding="utf-8")
        self.assertEqual(read_text_file(path), "Python is easy.")

    def test_empty_file_is_valid(self):
        path = self._write("empty.txt", "", encoding="utf-8")
        self.assertEqual(read_text_file(path), "")

    def test_missing_file_raises_friendly_error(self):
        # Assignment test case: "Missing file / Nonexistent path"
        missing = os.path.join(self.folder.name, "does_not_exist.txt")
        with self.assertRaises(TextFileError) as context:
            read_text_file(missing)
        self.assertIn("File not found", str(context.exception))

    def test_blank_path_rejected(self):
        for blank in ("", "   ", '""'):
            with self.subTest(path=repr(blank)):
                with self.assertRaises(TextFileError):
                    read_text_file(blank)

    def test_folder_instead_of_file(self):
        with self.assertRaises(TextFileError):
            read_text_file(self.folder.name)

    def test_quoted_path_from_drag_and_drop(self):
        path = self._write("quoted.txt", "hello", encoding="utf-8")
        self.assertEqual(read_text_file('"%s"' % path), "hello")

    def test_utf8_bom_is_removed(self):
        path = self._write("bom.txt", b"\xef\xbb\xbfHello", mode="wb")
        self.assertEqual(read_text_file(path), "Hello")

    def test_non_text_file_raises_friendly_error(self):
        path = self._write("binary.bin", b"\xff\xfe\x00\x81\x82\x83", mode="wb")
        with self.assertRaises(TextFileError) as context:
            read_text_file(path)
        self.assertIn("UTF-8", str(context.exception))

    def test_unicode_text_round_trip(self):
        path = self._write("uni.txt", "caf\u00e9 \u201cquoted\u201d", encoding="utf-8")
        self.assertEqual(read_text_file(path), "caf\u00e9 \u201cquoted\u201d")


class TestSaveReport(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)

    def test_writes_content_and_returns_absolute_path(self):
        target = os.path.join(self.folder.name, "analysis_report.txt")
        saved = save_report("REPORT BODY", target)
        self.assertTrue(os.path.isabs(saved))
        with open(saved, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "REPORT BODY")

    def test_overwrites_existing_report(self):
        target = os.path.join(self.folder.name, "analysis_report.txt")
        save_report("first", target)
        save_report("second", target)
        with open(target, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "second")

    def test_no_temp_file_left_behind(self):
        target = os.path.join(self.folder.name, "analysis_report.txt")
        save_report("x", target)
        self.assertEqual(os.listdir(self.folder.name), ["analysis_report.txt"])

    def test_unwritable_location_raises_friendly_error(self):
        bad = os.path.join(self.folder.name, "no_such_folder", "analysis_report.txt")
        with self.assertRaises(TextFileError):
            save_report("x", bad)

    def test_writes_unicode(self):
        target = os.path.join(self.folder.name, "u.txt")
        save_report("caf\u00e9 \u2014 done", target)
        with open(target, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "caf\u00e9 \u2014 done")


class TestCleanPath(unittest.TestCase):
    def test_strips_quotes_and_spaces(self):
        self.assertEqual(clean_path('  "C:\\notes\\a.txt"  '), "C:\\notes\\a.txt")
        self.assertEqual(clean_path("  'a.txt' "), "a.txt")


if __name__ == "__main__":
    unittest.main()
