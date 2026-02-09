"""Unit tests for create_summary script."""

import sys
from pathlib import Path

import pytest

# Import from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from create_summary import (
    first_letter_or_digraph,
    get_first_letters,
    remove_references,
    remove_verse_numbers,
)


class TestFirstLetterOrDigraph:
    """Tests for first_letter_or_digraph (Hungarian digraphs)."""

    def test_single_letter(self):
        assert first_letter_or_digraph("apa") == "a"
        assert first_letter_or_digraph("word") == "w"
        assert first_letter_or_digraph("In") == "I"

    def test_hungarian_digraphs(self):
        assert first_letter_or_digraph("csend") == "cs"
        assert first_letter_or_digraph("gyerek") == "gy"
        assert first_letter_or_digraph("lyuk") == "ly"
        assert first_letter_or_digraph("nyár") == "ny"
        assert first_letter_or_digraph("szép") == "sz"
        assert first_letter_or_digraph("tyúk") == "ty"
        assert first_letter_or_digraph("zsiráf") == "zs"

    def test_hungarian_digraphs_preserve_case(self):
        assert first_letter_or_digraph("CSEND") == "CS"
        assert first_letter_or_digraph("Szép") == "Sz"

    def test_empty_string(self):
        assert first_letter_or_digraph("") == ""


class TestRemoveVerseNumbers:
    """Tests for remove_verse_numbers."""

    def test_single_verse_number(self):
        assert remove_verse_numbers("1 In the beginning") == "In the beginning"
        assert remove_verse_numbers("2 And the earth was without form") == "And the earth was without form"

    def test_chapter_verse(self):
        assert remove_verse_numbers("3:16 For God so loved") == "For God so loved"
        assert remove_verse_numbers("1:1 In the beginning") == "In the beginning"

    def test_no_verse_number(self):
        assert remove_verse_numbers("In the beginning God created") == "In the beginning God created"

    def test_verse_with_dot(self):
        assert remove_verse_numbers("1. In the beginning") == "In the beginning"

    def test_verse_after_semicolon(self):
        assert remove_verse_numbers("igazat szól; 3 nyelvével nem") == "igazat szól; nyelvével nem"


class TestRemoveReferences:
    """Tests for remove_references."""

    def test_reference_at_end(self):
        assert remove_references("éjjel-nappal. Józs 1,8") == "éjjel-nappal."
        assert remove_references("word. J 1, 8") == "word."

    def test_reference_with_space(self):
        assert remove_references("Minden sikerül. Jer 17,8") == "Minden sikerül."

    def test_numbered_moses_references(self):
        # 1Móz, 2Móz, 3Móz, 5Móz (1st/2nd/3rd/5th Moses) are always references
        assert remove_references("Aki ezeket teszi. 3Móz 25,37; 5Móz 16,19") == "Aki ezeket teszi. ;"
        assert remove_references("text 1Móz 1,1 end") == "text end"

    def test_book_single_number_reference(self):
        # Zsolt 101 (Psalms 101) = book + single number, no comma
        assert remove_references("ha kárt vall is. Zsolt 101") == "ha kárt vall is."


class TestGetFirstLetters:
    """Tests for get_first_letters."""

    def test_simple_sentence(self):
        text = "In the beginning God created."
        assert get_first_letters(text) == "I t b G c."

    def test_punctuation_kept(self):
        text = "In the beginning, God created."
        assert get_first_letters(text) == "I t b, G c."

    def test_verse_number_removed(self):
        text = "1 In the beginning, God created."
        assert get_first_letters(text) == "I t b, G c."

    def test_chapter_verse_removed(self):
        text = "3:16 For God so loved the world."
        assert get_first_letters(text) == "F G s l t w."

    def test_hyphenation_kept(self):
        text = "word-one two-three"
        assert get_first_letters(text) == "w-o t-t"

    def test_hungarian_in_line(self):
        text = "csend és szép"
        assert get_first_letters(text) == "cs é sz"

    def test_multiline(self):
        text = "First line.\nSecond line."
        assert get_first_letters(text) == "F l.\nS l."

    def test_multiline_with_verse_numbers(self):
        text = "1 First verse.\n2 Second verse."
        assert get_first_letters(text) == "F v.\nS v."

    def test_empty_lines_removed(self):
        text = "One line.\n\nAnother."
        result = get_first_letters(text)
        assert result == "O l.\nA."

    def test_remove_verses_false(self):
        text = "1 In the beginning"
        # With remove_verses=True (default), "1 " is stripped
        assert get_first_letters(text, remove_verses=True) == "I t b"
        # With remove_verses=False, "1" is a token
        assert get_first_letters(text, remove_verses=False) == "1 I t b"

    def test_semicolon_followed_by_verse_number(self):
        # Psalm-15 style: sentence ends with ; then verse number then next sentence.
        # Output must have no space before semicolon and verse number must be removed.
        text = "Az, aki feddhetetlenül él, törekszik az igazságra, és szíve szerint igazat szól; 3 nyelvével nem rágalmaz."
        result = get_first_letters(text)
        assert result == "A, a f é, t a i, é sz sz i sz; ny n r."


class TestMainIntegration:
    """Integration tests running the script via subprocess."""

    def test_script_with_text_argument(self, tmp_path):
        import subprocess
        project_root = Path(__file__).resolve().parent.parent
        result = subprocess.run(
            [sys.executable, "create_summary.py", "In the beginning.", "-o", "out"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "I t b." in result.stdout
        out_file = project_root / "output" / "out.txt"
        assert out_file.exists()
        assert out_file.read_text() == "I t b."

    def test_script_with_file_input(self):
        import subprocess
        project_root = Path(__file__).resolve().parent.parent
        tests_input = project_root / "tests" / "input"
        tests_input.mkdir(parents=True, exist_ok=True)
        passage_file = tests_input / "tests_passage.txt"
        passage_file.write_text("For God so loved the world.")
        try:
            result = subprocess.run(
                [sys.executable, "create_summary.py", "-f", str(passage_file), "-o", "fromfile"],
                cwd=project_root,
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            assert "F G s l t w." in result.stdout
            out_file = project_root / "output" / "fromfile.txt"
            assert out_file.read_text() == "F G s l t w."
        finally:
            passage_file.unlink(missing_ok=True)
