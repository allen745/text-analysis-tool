"""Core text-analysis logic.

This module contains *pure functions only*: no input(), no print(), no file
access.  That keeps the logic easy to test and lets the menu (cli.py) and the
file handling (fileio.py) stay thin.

Only standard string / list / set / dict operations are used (assignment
requirement 6): lower(), strip(), split(), replace(), sets, dictionaries and
loops.  No external NLP library is imported.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

# Characters stripped from both ends of every word before counting.
# Includes typographic ("curly") quotes and dashes that appear in pasted text.
PUNCTUATION_CHARS = ".,;:!?\"'()[]{}<>-_/\\@#$%^&*+=~`|\u2026\u201c\u201d\u2018\u2019\u2014\u2013\u00ab\u00bb"

# Characters that always *separate* two words (never part of one), so they are
# replaced by a space before the text is split.  "?" and "!" can never sit
# inside a real word; dashes and slashes join two words into one token
# ("fast\u2014really") unless they are replaced.
WORD_SEPARATORS = ("?", "!", "...", "\u2026", "\u2014", "\u2013", "/", "\\", "|")

# Sentence boundaries, exactly as the assignment defines them.
SENTENCE_END = {".", "?", "!"}


# --------------------------------------------------------------------------
# Result container
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class AnalysisResult:
    """Everything the tool reports about one piece of text."""

    characters: int                 # includes spaces (requirement 2)
    words: int
    sentences: int
    unique_words: int
    frequencies: Dict[str, int]     # word -> number of occurrences
    top_words: List[str]            # every word tied for most frequent, A-Z
    top_frequency: int              # how often the top word(s) occur


# --------------------------------------------------------------------------
# Text preparation
# --------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Return *text* with line endings unified and edges tidied.

    * Windows ("\\r\\n") and old-Mac ("\\r") line endings become "\\n", so the
      same text gives the same character count on every operating system.
    * Trailing newlines are removed so a file saved with a final newline does
      not report one extra character.
    * Blank / whitespace-only text becomes "" (the "empty-text case").
    """
    if text is None:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.strip():
        return ""
    return text.rstrip("\n")


def extract_words(text: str) -> List[str]:
    """Split *text* into lowercase words with surrounding punctuation removed.

    Steps: replace separators with spaces -> lowercase -> split on whitespace
    -> strip punctuation from both ends of each token -> drop empty tokens.

    Punctuation *inside* a word is kept, so "don't" stays one word and "3.14"
    stays one number.
    """
    cleaned = text
    for separator in WORD_SEPARATORS:
        cleaned = cleaned.replace(separator, " ")

    words = []
    for token in cleaned.lower().split():
        token = token.strip(PUNCTUATION_CHARS)
        if token:                       # skip tokens that were only punctuation
            words.append(token)
    return words


# --------------------------------------------------------------------------
# Counting
# --------------------------------------------------------------------------

def _is_decimal_point(text: str, index: int) -> bool:
    """True if the "." at *index* sits between two digits, as in 3.14."""
    return (
        0 < index < len(text) - 1
        and text[index - 1].isdigit()
        and text[index + 1].isdigit()
    )


def count_sentences(text: str) -> int:
    """Count sentences. Boundaries are ".", "?" and "!" (assignment rule).

    Refinements that keep real-world text from being over-counted:

    * A run such as "?!" or "..." ends one sentence, not several.
    * A "." between two digits (3.14) is a decimal point, not a boundary.
    * Text after the last terminator ("Hello world") counts as a sentence.
    * A terminator with no words before it (a stray ".") counts for nothing.
    """
    count = 0
    has_content = False                 # does the current sentence hold a word?

    for index, char in enumerate(text):
        if char in SENTENCE_END:
            if char == "." and _is_decimal_point(text, index):
                continue
            if has_content:
                count += 1
                has_content = False
        elif char.isalnum():
            has_content = True

    if has_content:                     # trailing sentence with no terminator
        count += 1
    return count


def count_frequencies(words: List[str]) -> Dict[str, int]:
    """Return a dictionary mapping each word to how many times it occurs."""
    frequencies: Dict[str, int] = {}
    for word in words:
        frequencies[word] = frequencies.get(word, 0) + 1
    return frequencies


def find_most_frequent(frequencies: Dict[str, int]) -> Tuple[List[str], int]:
    """Return (all words tied for most frequent, their frequency).

    Ties are never hidden (requirement 3): every tied word is returned, in
    alphabetical order so the output is the same on every run.
    Empty input gives ([], 0).
    """
    if not frequencies:
        return [], 0
    highest = max(frequencies.values())
    tied = sorted(word for word, count in frequencies.items() if count == highest)
    return tied, highest


def sort_frequencies(frequencies: Dict[str, int]) -> List[Tuple[str, int]]:
    """Return (word, count) pairs: most frequent first, ties A-Z."""
    return sorted(frequencies.items(), key=lambda pair: (-pair[1], pair[0]))


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def analyze(text: str) -> AnalysisResult:
    """Analyse *text* and return an :class:`AnalysisResult`.

    Empty or blank text is a valid input and produces all-zero counts.
    """
    text = normalize_text(text)
    words = extract_words(text)
    frequencies = count_frequencies(words)
    top_words, top_frequency = find_most_frequent(frequencies)

    return AnalysisResult(
        characters=len(text),
        words=len(words),
        sentences=count_sentences(text),
        unique_words=len(set(words)),   # a set keeps each word only once
        frequencies=frequencies,
        top_words=top_words,
        top_frequency=top_frequency,
    )


def search_word(result: AnalysisResult, term: str) -> Tuple[str, int]:
    """Look up how often *term* appears. Returns (cleaned term, frequency).

    The term is cleaned exactly like the text itself (lowercase, punctuation
    removed), so "Python", "python" and "python." all find the same word.
    A word that is not in the text has frequency 0 (requirement 4).

    Raises ValueError if *term* is blank or contains more than one word.
    """
    candidates = extract_words(term)
    if len(candidates) != 1:
        raise ValueError("Please enter exactly one word to search for.")
    word = candidates[0]
    return word, result.frequencies.get(word, 0)
