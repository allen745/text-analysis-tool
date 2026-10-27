"""Generate test evidence for the assignment's acceptance checklist.

Run:   python run_evidence.py

It executes the five minimum test cases (assignment section F), the full
automated test suite, and three recorded menu sessions, then writes
everything to  evidence/evidence_report.txt  (plus a sample saved report).
Nothing is typed in by hand: every "actual" value below comes from running
the real code.
"""

import io
import os
import platform
import sys
import tempfile
import unittest
from datetime import datetime

from text_analyzer import analyzer, fileio
from text_analyzer.cli import TextAnalysisApp
from tests.helpers import ScriptedConsole

EVIDENCE_DIR = "evidence"
WIDTH = 72


def heading(title):
    return "\n%s\n%s\n%s\n" % ("=" * WIDTH, title, "=" * WIDTH)


def run_menu_session(answers, report_path):
    console = ScriptedConsole(answers)
    app = TextAnalysisApp(console.ask, console.show, report_path=report_path)
    app.run()
    return console.transcript


# --------------------------------------------------------------------------
# Section F: the five minimum test cases
# --------------------------------------------------------------------------

def minimum_test_cases():
    """Return a list of (scenario, input, expected, actual, passed)."""
    rows = []

    result = analyzer.analyze("Python is easy. Python is useful.")
    actual = "%d words, %d sentences; %s tied at %d" % (
        result.words, result.sentences, " and ".join(result.top_words), result.top_frequency)
    passed = (result.words == 6 and result.sentences == 2
              and result.top_words == ["is", "python"] and result.top_frequency == 2)
    rows.append(("Sample paragraph", "Python is easy. Python is useful.",
                 "6 words, 2 sentences; Python and is tied at 2", actual, passed))

    result = analyzer.analyze("PYTHON python Python")
    _, count = analyzer.search_word(result, "python")
    rows.append(("Mixed case", "PYTHON python Python", "Frequency python = 3",
                 "Frequency python = %d" % count, count == 3))

    result = analyzer.analyze("Hello, hello!")
    _, count = analyzer.search_word(result, "hello")
    rows.append(("Punctuation", "Hello, hello!", "Frequency hello = 2",
                 "Frequency hello = %d" % count, count == 2))

    try:
        result = analyzer.analyze("")
        actual = "chars %d, words %d, sentences %d, unique %d; no crash" % (
            result.characters, result.words, result.sentences, result.unique_words)
        passed = (result.characters, result.words, result.sentences, result.unique_words) == (0, 0, 0, 0)
    except Exception as error:                      # pragma: no cover
        actual, passed = "CRASHED: %r" % error, False
    rows.append(("Empty text", "(empty input)", "Counts 0; no crash", actual, passed))

    missing = os.path.join(tempfile.gettempdir(), "definitely_not_here_12345.txt")
    try:
        fileio.read_text_file(missing)
        actual, passed = "no error raised", False
    except fileio.TextFileError as error:
        actual, passed = "handled: \"%s\"" % error, True
    rows.append(("Missing file", "Nonexistent path",
                 "Error handled; menu remains usable", actual, passed))
    return rows


def format_cases(rows):
    lines = []
    for number, (scenario, given, expected, actual, passed) in enumerate(rows, 1):
        lines += [
            "Test %d: %s" % (number, scenario),
            "  Input    : %s" % given,
            "  Expected : %s" % expected,
            "  Actual   : %s" % actual,
            "  Result   : %s" % ("PASS" if passed else "FAIL"),
            "",
        ]
    return "\n".join(lines)


def run_unit_tests():
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover("tests", top_level_dir=".")
    outcome = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return stream.getvalue(), outcome


# --------------------------------------------------------------------------

def main():
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    work = tempfile.mkdtemp()
    report_path = os.path.join(work, "analysis_report.txt")

    rows = minimum_test_cases()
    unit_output, outcome = run_unit_tests()

    sample = run_menu_session(
        ["1", "Python is easy. Python is useful.", "", "3", "4", "5", "python", "5", "java", "6", "7"],
        report_path)
    with open(report_path, encoding="utf-8") as handle:
        saved_report = handle.read()

    missing_file = run_menu_session(
        ["2", os.path.join(work, "nonexistent.txt"), "1", "Hello, hello!", "", "5", "hello", "7"],
        report_path)
    empty = run_menu_session(["1", "", "3", "5", "anything", "6", "7"], report_path)

    all_passed = all(row[4] for row in rows) and outcome.wasSuccessful()

    out = [
        "WORD AND TEXT ANALYSIS TOOL - TEST EVIDENCE",
        "CVM University | Course 102040306 | Project P10",
        "Generated : %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Python    : %s on %s" % (platform.python_version(), platform.system()),
        "",
        "OVERALL: %s  (%d/%d assignment cases, %d/%d automated tests)" % (
            "ALL PASSED" if all_passed else "FAILURES PRESENT",
            sum(1 for row in rows if row[4]), len(rows),
            outcome.testsRun - len(outcome.failures) - len(outcome.errors), outcome.testsRun),
        heading("SECTION F - MINIMUM TEST CASES (from the assignment sheet)"),
        format_cases(rows),
        heading("SECTION E - SAMPLE RUN: recorded menu session"),
        sample,
        heading("MISSING FILE: error is shown and the menu stays usable"),
        missing_file,
        heading("EMPTY TEXT: counts are zero and nothing crashes"),
        empty,
        heading("SAVED FILE: contents of analysis_report.txt from the sample run"),
        saved_report,
        heading("AUTOMATED TEST SUITE (python -m unittest, verbose)"),
        unit_output,
    ]
    with open(os.path.join(EVIDENCE_DIR, "evidence_report.txt"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(out))
    with open(os.path.join(EVIDENCE_DIR, "sample_analysis_report.txt"), "w", encoding="utf-8") as handle:
        handle.write(saved_report)

    print(format_cases(rows))
    print("Automated tests: %d run, %d failed" % (outcome.testsRun, len(outcome.failures) + len(outcome.errors)))
    print("Evidence written to %s/" % EVIDENCE_DIR)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
