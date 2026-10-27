# Word and Text Analysis Tool

**CVM University, Faculty of Engineering & Technology**
Course 102040306: Introduction to Python Programming
Project **P10**: Word and Text Analysis Tool (Syllabus U4, U5, U6; SLO-4, SLO-5, SLO-6)

A menu-driven Python program that analyses a typed paragraph or a text file and
reports character, word and sentence counts, unique words, word frequencies,
the most frequent word(s), and lets you search for any word and save a report.

Python standard library only. No external NLP libraries (requirement 6).
Developed and tested on Python 3.12 (Linux). The code uses no feature newer than
Python 3.7 and no OS-specific calls, so it should run on Windows and macOS too.

---

## Run it

```bash
python main.py
```

(or `python -m text_analyzer`)

```
==== Word and Text Analysis Tool ====
  1. Input text
  2. Read text file
  3. Show text statistics
  4. Show word frequency
  5. Search for a word
  6. Save summary to analysis_report.txt
  7. Exit
```

Try the files in `samples/`: option 2, then type `samples/sample.txt`.

## Test it

```bash
python -m unittest discover -s tests -t .      # 63 automated tests
python run_evidence.py                          # regenerates evidence/
```

`run_evidence.py` runs the five test cases from section F of the assignment
sheet, the full test suite and three recorded menu sessions, and writes the
results to **`evidence/evidence_report.txt`**. This is the evidence to attach
for the acceptance checklist.

---

## Mandatory requirements (section B) and where each one lives

| # | Requirement | Where it is implemented |
|---|-------------|-------------------------|
| 1 | Input text and Read text file modes; unreadable file shows an error and returns to the menu | `cli.py`: `input_text()`, `read_file()`; `fileio.py`: `read_text_file()` raises `TextFileError`, which the menu catches |
| 2 | Character count (with spaces), word count, sentence count (`.` `?` `!`) | `analyzer.py`: `analyze()`, `count_sentences()` |
| 3 | Lowercase, remove punctuation, count; show most frequent word, **all** words on a tie | `analyzer.py`: `extract_words()`, `count_frequencies()`, `find_most_frequent()` |
| 4 | Search a word and report its frequency; absent word gives 0 | `analyzer.py`: `search_word()` uses `dict.get(word, 0)` |
| 5 | Save summary to `analysis_report.txt`; blank input is valid and reports zeros | `cli.py`: `save()`; `report.py`: `format_report()`; `fileio.py`: `save_report()` |
| 6 | No external NLP libraries | Only `os`, `datetime`, `dataclasses`, `typing` are imported |

## Python concepts that must be visible (section G)

| Concept | Where to point the examiner |
|---------|-----------------------------|
| String creation and methods | `analyzer.py`: `PUNCTUATION_CHARS`, `normalize_text()` |
| `lower()`, `strip()`, `split()`, `replace()` | `extract_words()` uses all four in sequence |
| Sets | `analyze()`: `len(set(words))` gives the unique-word count; `SENTENCE_END = {".", "?", "!"}` |
| Dictionaries | `count_frequencies()` builds `{word: count}`; `search_word()` reads it |
| Loops | `count_sentences()` (character loop), `extract_words()`, `run()` (menu loop) |
| Functions | Every feature is a small, documented function with type hints |
| File reading / writing | `fileio.py`: `read_text_file()`, `save_report()` |
| Exceptions | `fileio.py`: `FileNotFoundError`, `PermissionError`, `UnicodeDecodeError`, `OSError`, converted to `TextFileError`; `cli.py`: `ValueError`, `EOFError` |

## Test cases (section F)

| Scenario | Input | Expected | Result |
|----------|-------|----------|--------|
| Sample paragraph | `Python is easy. Python is useful.` | 6 words, 2 sentences; Python and is tied at 2 | PASS |
| Mixed case | `PYTHON python Python` | frequency python = 3 | PASS |
| Punctuation | `Hello, hello!` | frequency hello = 2 | PASS |
| Empty text | empty input | counts 0; no crash | PASS |
| Missing file | nonexistent path | error handled; menu remains usable | PASS |

Full recorded output: `evidence/evidence_report.txt`.

---

## Project structure

```
text_analysis_tool/
├── main.py                  entry point
├── run_evidence.py          generates the test evidence
├── text_analyzer/
│   ├── analyzer.py          pure logic: counting, frequencies, search (no I/O)
│   ├── fileio.py            reading files, saving the report, error handling
│   ├── report.py            formatting for screen and saved file
│   └── cli.py               menu loop
├── tests/                   63 unittest tests (logic, files, whole menu)
├── samples/                 ready-made inputs, including an empty file
└── evidence/                generated test evidence
```

**Design principle:** `analyzer.py` never calls `input()`, `print()` or opens a
file. That is why every rule can be tested directly, and why the menu itself
can be tested by feeding it scripted answers (`tests/helpers.py`).

## Design decisions (good to know for the viva)

* **What counts as a word.** Text is lowercased, then split on whitespace, then
  punctuation is stripped from both ends of each token. Punctuation *inside* a
  word is kept, so `don't` and `well-known` stay whole words and `3.14` stays
  one number. `?`, `!`, `...` and em/en dashes always separate words, so
  `wait...what` is two words.
* **What counts as a sentence.** Boundaries are `.`, `?` and `!`, as the
  assignment says. A run like `?!` or `...` is one boundary; a `.` between two
  digits (`3.14`) is a decimal point, not a boundary; trailing text with no
  final punctuation counts as one sentence.
* **Ties.** Every tied word is shown, alphabetically, so output is the same on
  every run.
* **Blank input.** Empty or whitespace-only text is the valid "empty text" case
  and reports zeros. It is distinct from "nothing loaded yet", where analysis
  options ask you to load text first.
* **Line endings.** Windows `\r\n` is normalised to `\n` and trailing newlines
  are dropped, so a file gives the same character count on every system.
* **Safe saving.** The report is written to a temporary file and then moved into
  place, so a failure can never leave a half-written report.

## Known limitations

* Abbreviations such as `Dr.` or `e.g.` are counted as sentence endings,
  because the assignment defines boundaries purely by punctuation.
* Typed input ends at the first blank line, so use option 2 (file) for text
  that contains blank lines between paragraphs.
* Files must be UTF-8 text and no larger than 10 MB.
