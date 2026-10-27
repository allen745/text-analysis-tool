"""Turns an AnalysisResult into readable text (screen summary and saved file)."""

from typing import Dict, Optional

from .analyzer import AnalysisResult, sort_frequencies

LINE = "=" * 52
THIN = "-" * 52


def format_statistics(result: AnalysisResult) -> str:
    """The counts block: characters, words, sentences, unique, top word(s)."""
    if result.top_words:
        shown = ", ".join(result.top_words)
        suffix = "  (tied)" if len(result.top_words) > 1 else ""
        top_line = "%s%s" % (shown, suffix)
        top_count = str(result.top_frequency)
    else:
        top_line = "None (no words found)"
        top_count = "0"

    rows = [
        ("Characters (with spaces)", str(result.characters)),
        ("Words", str(result.words)),
        ("Sentences", str(result.sentences)),
        ("Unique words", str(result.unique_words)),
        ("Most frequent word(s)", top_line),
        ("Highest frequency", top_count),
    ]
    label_width = max(len(label) for label, _ in rows)
    return "\n".join("%-*s : %s" % (label_width, label, value) for label, value in rows)


def format_frequency_table(result: AnalysisResult, limit: Optional[int] = None) -> str:
    """A word | count table, most frequent first. *limit* caps the rows."""
    if not result.frequencies:
        return "(no words to show)"

    rows = sort_frequencies(result.frequencies)
    hidden = 0
    if limit is not None and len(rows) > limit:
        hidden = len(rows) - limit
        rows = rows[:limit]

    width = max(len("Word"), max(len(word) for word, _ in rows))
    lines = ["%-*s  %s" % (width, "Word", "Count"), "%s  %s" % ("-" * width, "-----")]
    for word, count in rows:
        lines.append("%-*s  %d" % (width, word, count))
    if hidden:
        lines.append("... and %d more (save the report to see all)" % hidden)
    return "\n".join(lines)


def format_report(
    result: AnalysisResult,
    source_label: str,
    generated_at: str,
    searches: Optional[Dict[str, int]] = None,
) -> str:
    """The full text saved to analysis_report.txt."""
    parts = [
        LINE,
        "        WORD AND TEXT ANALYSIS REPORT",
        LINE,
        "Generated : %s" % generated_at,
        "Source    : %s" % source_label,
        "",
        "TEXT STATISTICS",
        THIN,
        format_statistics(result),
        "",
        "WORD FREQUENCY (all words)",
        THIN,
        format_frequency_table(result),
    ]

    if searches:
        parts += ["", "WORDS SEARCHED THIS SESSION", THIN]
        for word, count in searches.items():
            parts.append("%s : %d" % (word, count))

    parts += ["", LINE, ""]
    return "\n".join(parts)
