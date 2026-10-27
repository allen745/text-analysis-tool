"""Menu-driven command-line interface.

The application reads input and writes output through two functions passed
into the constructor (``input_fn`` and ``output_fn``).  In normal use these
are the built-in ``input`` and ``print``; the automated tests substitute
scripted versions, which is how the whole menu is tested without a human.
"""

from datetime import datetime
from typing import Callable, Dict, Optional

from . import analyzer, fileio, report

MENU = """
==== Word and Text Analysis Tool ====
  1. Input text
  2. Read text file
  3. Show text statistics
  4. Show word frequency
  5. Search for a word
  6. Save summary to analysis_report.txt
  7. Exit"""

TABLE_ROWS_ON_SCREEN = 20


class TextAnalysisApp:
    """Holds the current text and runs the menu loop."""

    def __init__(
        self,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
        report_path: str = fileio.REPORT_FILENAME,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._input = input_fn
        self._output = output_fn
        self._report_path = report_path
        self._clock = clock

        self.result: Optional[analyzer.AnalysisResult] = None   # None = nothing loaded
        self.source_label = ""
        self.searches: Dict[str, int] = {}

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> int:
        """Show the menu until the user exits. Returns a process exit code."""
        self._output("Welcome to the Word and Text Analysis Tool.")
        actions = {
            1: self.input_text,
            2: self.read_file,
            3: self.show_statistics,
            4: self.show_frequency,
            5: self.search,
            6: self.save,
        }
        try:
            while True:
                self._output(MENU)
                choice = self._ask_menu_choice()
                if choice == 7:
                    self._output("Goodbye!")
                    return 0
                if choice is None:
                    continue
                actions[choice]()
        except (EOFError, KeyboardInterrupt):
            # Ctrl+D / Ctrl+C / closed input: leave cleanly, no traceback.
            self._output("\nInput closed. Goodbye!")
            return 0

    def _ask_menu_choice(self) -> Optional[int]:
        """Read the menu option; return None (after a message) if invalid."""
        raw = self._input("Choose an option (1-7): ").strip()
        try:
            choice = int(raw)
        except ValueError:
            self._output("Invalid choice. Please type a number from 1 to 7.")
            return None
        if choice < 1 or choice > 7:
            self._output("Invalid choice. Please type a number from 1 to 7.")
            return None
        return choice

    # ------------------------------------------------------------------
    # Loading text
    # ------------------------------------------------------------------

    def input_text(self) -> None:
        """Menu 1: type or paste text. A blank first line means empty text."""
        self._output("Type or paste your text. Press Enter on an empty line to finish.")
        self._output("(Finishing straight away analyses empty text: all counts are 0.)")
        lines = []
        while True:
            line = self._input("> ")
            if not line.strip():
                break
            lines.append(line)
        self._load("\n".join(lines), "Typed text")

    def read_file(self) -> None:
        """Menu 2: read a text file. On any failure show why and return."""
        raw_path = self._input("Enter the path of the text file: ")
        try:
            text = fileio.read_text_file(raw_path)
        except fileio.TextFileError as error:
            self._output("Error: %s" % error)
            self._output("Returning to the menu.")
            return
        self._load(text, "File: %s" % fileio.clean_path(raw_path))

    def _load(self, text: str, source_label: str) -> None:
        """Analyse *text*, remember it, and show the statistics."""
        self.result = analyzer.analyze(text)
        self.source_label = source_label
        self.searches = {}                      # old searches belong to old text
        if self.result.characters == 0:
            self._output("\nThe text is empty, so every count is zero.")
        else:
            self._output("\nText loaded (%s)." % source_label)
        self._output(report.format_statistics(self.result))

    # ------------------------------------------------------------------
    # Using the loaded text
    # ------------------------------------------------------------------

    def _require_text(self) -> bool:
        """True if text is loaded; otherwise tell the user what to do."""
        if self.result is None:
            self._output("No text loaded yet. Use option 1 or 2 first.")
            return False
        return True

    def show_statistics(self) -> None:
        """Menu 3."""
        if not self._require_text():
            return
        self._output("\n" + report.format_statistics(self.result))

    def show_frequency(self) -> None:
        """Menu 4."""
        if not self._require_text():
            return
        self._output("\n" + report.format_frequency_table(self.result, TABLE_ROWS_ON_SCREEN))

    def search(self) -> None:
        """Menu 5: report how often one word occurs (0 if absent)."""
        if not self._require_text():
            return
        term = self._input("Enter the word to search for: ")
        try:
            word, count = analyzer.search_word(self.result, term)
        except ValueError as error:
            self._output("Error: %s" % error)
            return
        self.searches[word] = count
        self._output("'%s' appears %d time(s)." % (word, count))

    def save(self) -> None:
        """Menu 6: write the summary to analysis_report.txt."""
        if not self._require_text():
            return
        stamp = self._clock().strftime("%Y-%m-%d %H:%M:%S")
        content = report.format_report(self.result, self.source_label, stamp, self.searches)
        try:
            saved_to = fileio.save_report(content, self._report_path)
        except fileio.TextFileError as error:
            self._output("Error: %s" % error)
            return
        self._output("Report saved to: %s" % saved_to)


def main() -> int:
    """Entry point used by main.py and ``python -m text_analyzer``."""
    return TextAnalysisApp().run()
