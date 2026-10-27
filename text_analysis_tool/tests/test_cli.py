"""End-to-end tests of the menu, driven by scripted user input."""

import os
import re
import tempfile
import unittest
from datetime import datetime

from text_analyzer.cli import TextAnalysisApp
from tests.helpers import ScriptedConsole

FIXED_TIME = datetime(2026, 1, 15, 10, 30, 0)


class CliTestCase(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.report_path = os.path.join(self.folder.name, "analysis_report.txt")

    def run_session(self, answers):
        console = ScriptedConsole(answers)
        app = TextAnalysisApp(
            input_fn=console.ask,
            output_fn=console.show,
            report_path=self.report_path,
            clock=lambda: FIXED_TIME,
        )
        exit_code = app.run()
        return console, exit_code

    def assertShows(self, console, pattern):
        self.assertRegex(console.transcript, pattern)


class TestHappyPath(CliTestCase):
    def test_sample_paragraph_full_session(self):
        console, code = self.run_session([
            "1", "Python is easy. Python is useful.", "",   # input text
            "5", "python",                                  # search
            "5", "java",                                    # absent word
            "6",                                            # save
            "7",                                            # exit
        ])
        self.assertEqual(code, 0)
        self.assertShows(console, r"Words\s+: 6")
        self.assertShows(console, r"Sentences\s+: 2")
        self.assertShows(console, r"is, python\s+\(tied\)")
        self.assertShows(console, r"'python' appears 2 time\(s\)")
        self.assertShows(console, r"'java' appears 0 time\(s\)")
        self.assertShows(console, "Report saved to")

    def test_saved_report_contents(self):
        self.run_session(["1", "Python is easy. Python is useful.", "", "5", "python", "6", "7"])
        with open(self.report_path, encoding="utf-8") as handle:
            body = handle.read()
        self.assertIn("2026-01-15 10:30:00", body)
        self.assertIn("Source    : Typed text", body)
        self.assertRegex(body, r"Words\s+: 6")
        self.assertRegex(body, r"Sentences\s+: 2")
        self.assertRegex(body, r"python\s+2")
        self.assertIn("python : 2", body)       # the searched word is recorded

    def test_read_file_mode(self):
        path = os.path.join(self.folder.name, "in.txt")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("Hello, hello!\n")
        console, _ = self.run_session(["2", path, "5", "hello", "7"])
        self.assertShows(console, r"'hello' appears 2 time\(s\)")
        self.assertShows(console, r"Characters \(with spaces\)\s+: 13")

    def test_frequency_table_option(self):
        console, _ = self.run_session(["1", "b a a", "", "4", "7"])
        self.assertShows(console, r"a\s+2")
        self.assertShows(console, r"b\s+1")


class TestEdgeCases(CliTestCase):
    def test_empty_text_reports_zeros(self):
        console, code = self.run_session(["1", "", "3", "6", "7"])
        self.assertEqual(code, 0)
        self.assertShows(console, "text is empty")
        self.assertShows(console, r"Words\s+: 0")
        self.assertShows(console, r"Most frequent word\(s\)\s+: None")
        self.assertTrue(os.path.exists(self.report_path))   # blank text can be saved

    def test_missing_file_returns_to_menu(self):
        bad = os.path.join(self.folder.name, "nope.txt")
        console, code = self.run_session(["2", bad, "7"])
        self.assertEqual(code, 0)
        self.assertShows(console, "Error: File not found")
        self.assertShows(console, "Returning to the menu")
        self.assertEqual(console.count_menus(), 2)           # menu came back

    def test_menu_stays_usable_after_missing_file(self):
        bad = os.path.join(self.folder.name, "nope.txt")
        console, _ = self.run_session(["2", bad, "1", "Hello, hello!", "", "5", "hello", "7"])
        self.assertShows(console, r"'hello' appears 2 time\(s\)")

    def test_invalid_menu_choices(self):
        console, code = self.run_session(["abc", "", "0", "9", "-1", "3.5", "7"])
        self.assertEqual(code, 0)
        self.assertEqual(console.transcript.count("Invalid choice"), 6)

    def test_actions_before_loading_text(self):
        console, _ = self.run_session(["3", "4", "5", "6", "7"])
        self.assertEqual(console.transcript.count("No text loaded yet"), 4)
        self.assertFalse(os.path.exists(self.report_path))

    def test_bad_search_terms(self):
        console, _ = self.run_session(["1", "hi there", "", "5", "", "5", "two words", "7"])
        self.assertEqual(console.transcript.count("exactly one word"), 2)

    def test_multi_line_input(self):
        console, _ = self.run_session(["1", "First line.", "Second line.", "", "3", "7"])
        self.assertShows(console, r"Sentences\s+: 2")

    def test_loading_new_text_clears_old_searches(self):
        self.run_session(["1", "cat", "", "5", "cat", "1", "dog", "", "6", "7"])
        with open(self.report_path, encoding="utf-8") as handle:
            body = handle.read()
        self.assertNotIn("cat : 1", body)
        self.assertNotIn("WORDS SEARCHED", body)

    def test_closed_input_exits_cleanly(self):
        # Script ends without choosing Exit -> EOFError -> clean exit, no traceback
        console, code = self.run_session(["1", "Hello", ""])
        self.assertEqual(code, 0)
        self.assertShows(console, "Goodbye")

    def test_save_failure_is_reported_not_raised(self):
        self.report_path = os.path.join(self.folder.name, "missing_dir", "r.txt")
        console, code = self.run_session(["1", "Hi.", "", "6", "7"])
        self.assertEqual(code, 0)
        self.assertShows(console, "Error: Could not save the report")


if __name__ == "__main__":
    unittest.main()
