"""Tests for text_analyzer.analyzer.

The first five tests are the assignment's "Minimum test cases" (section F),
named after the scenario they cover.  The rest are edge cases that real text
produces.
"""

import unittest

from text_analyzer.analyzer import (
    analyze,
    count_sentences,
    extract_words,
    find_most_frequent,
    search_word,
    sort_frequencies,
)


class AssignmentMinimumTestCases(unittest.TestCase):
    """Section F of the assignment sheet."""

    def test_sample_paragraph(self):
        # Input: "Python is easy. Python is useful."
        # Expected: 6 words, 2 sentences, Python and is tied at 2
        result = analyze("Python is easy. Python is useful.")
        self.assertEqual(result.words, 6)
        self.assertEqual(result.sentences, 2)
        self.assertEqual(result.frequencies["python"], 2)
        self.assertEqual(result.frequencies["is"], 2)
        self.assertEqual(result.top_words, ["is", "python"])
        self.assertEqual(result.top_frequency, 2)

    def test_mixed_case(self):
        # Input: "PYTHON python Python"  ->  frequency python = 3
        result = analyze("PYTHON python Python")
        self.assertEqual(search_word(result, "python"), ("python", 3))

    def test_punctuation(self):
        # Input: "Hello, hello!"  ->  frequency hello = 2
        result = analyze("Hello, hello!")
        self.assertEqual(search_word(result, "hello"), ("hello", 2))

    def test_empty_text(self):
        # Input: empty  ->  counts 0, no crash
        for blank in ("", "   ", "\n\n", "\t \n"):
            with self.subTest(blank=repr(blank)):
                result = analyze(blank)
                self.assertEqual(result.characters, 0)
                self.assertEqual(result.words, 0)
                self.assertEqual(result.sentences, 0)
                self.assertEqual(result.unique_words, 0)
                self.assertEqual(result.top_words, [])
                self.assertEqual(result.top_frequency, 0)
                self.assertEqual(result.frequencies, {})

    # "Missing file" is covered in test_fileio.py (TestReadTextFile) and in
    # test_cli.py (test_missing_file_returns_to_menu).


class CharacterCount(unittest.TestCase):
    def test_includes_spaces(self):
        self.assertEqual(analyze("Python is easy. Python is useful.").characters, 33)

    def test_trailing_newline_is_not_counted(self):
        self.assertEqual(analyze("Hi.\n").characters, 3)

    def test_windows_line_endings_match_unix(self):
        self.assertEqual(analyze("a.\r\nb.").characters, analyze("a.\nb.").characters)


class SentenceCounting(unittest.TestCase):
    def test_period_question_exclamation(self):
        self.assertEqual(count_sentences("One. Two? Three!"), 3)

    def test_repeated_terminators_are_one_boundary(self):
        self.assertEqual(count_sentences("Really?! Yes... okay."), 3)

    def test_decimal_point_is_not_a_boundary(self):
        self.assertEqual(count_sentences("Pi is 3.14. It is nice."), 2)

    def test_text_without_terminator_is_one_sentence(self):
        self.assertEqual(count_sentences("Hello world"), 1)

    def test_stray_terminators_count_for_nothing(self):
        self.assertEqual(count_sentences("... ?! ."), 0)

    def test_empty(self):
        self.assertEqual(count_sentences(""), 0)

    def test_sentences_across_lines(self):
        self.assertEqual(count_sentences("First line.\nSecond line."), 2)


class WordExtraction(unittest.TestCase):
    def test_lowercases_and_strips_punctuation(self):
        self.assertEqual(extract_words('"Hello," she said.'), ["hello", "she", "said"])

    def test_keeps_internal_apostrophe(self):
        self.assertEqual(extract_words("Don't stop"), ["don't", "stop"])

    def test_keeps_hyphenated_word_together(self):
        self.assertEqual(extract_words("A well-known fact"), ["a", "well-known", "fact"])

    def test_em_dash_separates_words(self):
        self.assertEqual(extract_words("fast\u2014really fast"), ["fast", "really", "fast"])

    def test_curly_quotes_removed(self):
        self.assertEqual(extract_words("\u201cHello\u201d \u2018there\u2019"), ["hello", "there"])

    def test_ellipsis_between_words(self):
        self.assertEqual(extract_words("wait...what"), ["wait", "what"])

    def test_lone_punctuation_is_not_a_word(self):
        self.assertEqual(extract_words("a - b ... c"), ["a", "b", "c"])

    def test_numbers_are_words(self):
        self.assertEqual(extract_words("Pi is 3.14"), ["pi", "is", "3.14"])

    def test_extra_whitespace_and_newlines(self):
        self.assertEqual(extract_words("  a \n\n b\t c  "), ["a", "b", "c"])


class MostFrequent(unittest.TestCase):
    def test_single_winner(self):
        self.assertEqual(find_most_frequent({"a": 3, "b": 1}), (["a"], 3))

    def test_three_way_tie_is_alphabetical(self):
        self.assertEqual(find_most_frequent({"c": 2, "a": 2, "b": 2}), (["a", "b", "c"], 2))

    def test_empty(self):
        self.assertEqual(find_most_frequent({}), ([], 0))

    def test_sort_order(self):
        pairs = sort_frequencies({"b": 1, "a": 1, "z": 5})
        self.assertEqual(pairs, [("z", 5), ("a", 1), ("b", 1)])


class SearchWord(unittest.TestCase):
    def setUp(self):
        self.result = analyze("Python is easy. Python is useful.")

    def test_absent_word_is_zero(self):
        self.assertEqual(search_word(self.result, "java"), ("java", 0))

    def test_case_insensitive(self):
        self.assertEqual(search_word(self.result, "PyThOn")[1], 2)

    def test_term_with_punctuation(self):
        self.assertEqual(search_word(self.result, "easy.")[1], 1)

    def test_search_in_empty_text_is_zero(self):
        self.assertEqual(search_word(analyze(""), "anything"), ("anything", 0))

    def test_blank_term_rejected(self):
        for bad in ("", "   ", "!!!"):
            with self.subTest(term=bad):
                with self.assertRaises(ValueError):
                    search_word(self.result, bad)

    def test_multi_word_term_rejected(self):
        with self.assertRaises(ValueError):
            search_word(self.result, "python is")


class RealisticParagraph(unittest.TestCase):
    def test_multi_line_paragraph(self):
        text = (
            "Data is the new oil. Is data really that valuable? Yes!\n"
            "Well-known firms collect data every day, and they analyse the data carefully."
        )
        result = analyze(text)
        self.assertEqual(result.sentences, 4)
        self.assertEqual(result.frequencies["data"], 4)
        self.assertEqual(result.top_words, ["data"])
        self.assertEqual(result.frequencies["well-known"], 1)


if __name__ == "__main__":
    unittest.main()
