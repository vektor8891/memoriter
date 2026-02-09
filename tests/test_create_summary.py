"""Unit tests for create_summary script."""

import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    pytest = None

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

    def test_single_digit_verse_number_in_middle_removed(self):
        # After ref removal, "fű: ref; ref; 6 reggel" becomes "fű:  6 reggel"; verse number stripped
        assert remove_verse_numbers("fű  6 reggel virágzik") == "fű reggel virágzik"

    def test_leading_debris_after_ref_fragment_stripped(self):
        # Leftover from ref like "Zsolt 18,31; 119,130": leading digits removed leave ",130 9 ";
        # MID removal leaves ", 9 " or ", 130 ". New cleanup strips this so no leading ", 9 " in result.
        assert remove_verse_numbers(", 9 Az Úr rendelkezései helyesek.") == "Az Úr rendelkezései helyesek."
        assert remove_verse_numbers(", 130 9 Az Úr parancsolata.") == "Az Úr parancsolata."
        assert remove_verse_numbers("; 119,130 9 Az Úr törvénye.") == "Az Úr törvénye."


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

    def test_comma_semicolon_debris_after_two_refs_removed(self):
        # "text, Zsolt 34,8; Mt 4,6" -> refs removed leave ", ; "; strip to ", "
        assert remove_references("minden utadon, Zsolt 34,8; Mt 4,6") == "minden utadon,"
        assert remove_references("utadon, Zsolt 34,8; Mt 4,6 kézen") == "utadon, kézen"

    def test_leading_semicolon_after_refs_removed(self):
        # Ref list "Zsolt 73,26; JSir 3,24" leaves "; " before next sentence; strip it
        assert remove_references(" Zsolt 73,26; JSir 3,24") == ""
        assert remove_references(" ; 6 Osztályrészem kies helyre esett.") == "6 Osztályrészem kies helyre esett."

    def test_verse_range_in_reference(self):
        # ApCsel 2,25-28 (Acts 2:25-28) should be removed as a single reference
        assert remove_references("Text. ApCsel 2,25-28 end") == "Text. end"
        assert remove_references("ApCsel 2,25-28") == ""

    def test_leftover_debris_after_ref_removal(self):
        # Verse range remainder "-28; 13,35; " and continuation ref "13,35; " without book name
        assert remove_references("-28; 13,35; Ezért örül a szívem.") == "Ezért örül a szívem."
        assert remove_references(" ; 13,35; Zsolt 109,31") == ""
        assert remove_references(" -28; 13,35; 9 Ezért örül.") == "9 Ezért örül."

    def test_orphan_ref_fragment_at_end_removed(self):
        # Psalm 107 style: "..., Ézs 35,10; 43,5-6" — book ref removed leaves ", 43,5-6"; strip it
        assert remove_references("Így szóljanak az Úr megváltottai, akiket megváltott az ellenség kezéből, Ézs 35,10; 43,5-6") == (
            "Így szóljanak az Úr megváltottai, akiket megváltott az ellenség kezéből"
        )

    def test_orphan_ref_fragment_followed_by_verse_number_removed(self):
        # Merged sentence: "... Ézs 35,10; 43,5-6 3 és össze..." — remove ", 43,5-6 " before verse number
        assert remove_references("Így szóljanak az Úr megváltottai, akiket megváltott az ellenség kezéből, Ézs 35,10; 43,5-6 3 és összegyűjtött") == (
            "Így szóljanak az Úr megváltottai, akiket megváltott az ellenség kezéből 3 és összegyűjtött"
        )

    def test_colon_kept_after_ref_list(self):
        # "word: ref; ref; ref" -> "word:" (semicolons removed, colon kept)
        assert remove_references("mint a növekvő fű: Jób 14,1-2; Ézs 40,6-7; 1Pt 1,24") == "mint a növekvő fű:"
        # Single ref with following text: ref removed, colon and rest kept
        assert remove_references("text: ApCsel 2,25 end") == "text: end"


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

    def test_ref_list_then_verse_no_leading_debris(self):
        # Psalm-16 style: sentence ends with ref list (verse range + continuation refs), then next verse.
        # Output must not start with "; " or "- 2;,; " from reference leftovers.
        text = (
            "5 Uram, te vagy osztályrészem és poharam, te tartod kezedben sorsomat. Zsolt 73,26; JSir 3,24\n\n"
            "6 Osztályrészem kies helyre esett, örökségem nagyon tetszik nekem."
        )
        result = get_first_letters(text)
        assert "O k h e, ö n t n." in result
        assert result.count("; O k h e") == 0  # no leading semicolon before this line

    def test_verse_range_ref_list_then_verse_no_leading_debris(self):
        # Ref list with verse range (ApCsel 2,25-28) and "; 13,35; Zsolt 109,31" then next verse
        text = (
            "8 Az Úrra tekintek szüntelen, nem tántorodom meg, mert a jobbomon van. "
            "ApCsel 2,25-28; 13,35; Zsolt 109,31\n\n"
            "9 Ezért örül a szívem, és ujjong a lelkem, testem is biztonságban van."
        )
        result = get_first_letters(text)
        assert "E ö a sz, é u a l, t i b v." in result
        assert "- 2;,;" not in result and "- 2 ; , ;" not in result  # no leftover ref debris

    def test_orphan_verse_ref_fragment_no_leading_debris(self):
        # Psalm-19 style: "Zsolt 18,31; 119,130" — only first ref has book name; "119,130" stays.
        # After verse removal we get leading ", 9 " or ", 130 ". Output must not start with ", 9 ".
        text = (
            "8 Az Úr törvénye tökéletes, felüdíti a lelket. Zsolt 18,31; 119,130\n"
            "9 Az Úr rendelkezései helyesek, megörvendeztetik a szívet."
        )
        result = get_first_letters(text)
        # Second sentence's first letters must be "A Ú r h, m a sz." with no leading ", 9 "
        assert "A Ú r h, m a sz." in result
        assert ", 9 A Ú r h" not in result

    def test_selah_szela_removed_no_debris(self):
        # (Szela.) / (Sz.) are liturgical pause markers, not part of the psalm; must be stripped.
        # No "( Sz .)" line and no stray verse number in the next sentence.
        text = (
            "6 Ilyen az a nemzedék, amely hozzá folyamodik, akik Jákób Istenének orcáját keresik. (Szela.)\n"
            "7 Emeljétek föl fejeteket, ti, kapuk, emelkedjetek föl, ti, ősi ajtók, hogy bemehessen a dicső király!"
        )
        result = get_first_letters(text)
        assert "( Sz .)" not in result
        assert "7 E f f" not in result
        assert "E f f, t, k, e f, t, ő a, h b a d k!" in result

    def test_selah_at_end_removed(self):
        # Trailing (Szela.) or (Sz.) must not produce a separate line.
        text = "Ki az a dicső király? A Seregek Ura, ő a dicső király! (Szela.)"
        result = get_first_letters(text)
        assert result.strip().endswith("k!")
        assert "( Sz .)" not in result

    def test_sz_abbrev_removed(self):
        # (Sz.) abbreviation for Szela also removed
        text = "First line. (Sz.) 2 Second line."
        result = get_first_letters(text)
        assert "( Sz .)" not in result
        assert "S l." in result

    def test_quotation_marks_spacing(self):
        # Hungarian „ and ": space after : before „; no space after „; no space before "; space after " before next word
        text = "A karmesternek: „A szőlőtaposók” kezdetű ének dallamára."
        result = get_first_letters(text)
        expected = "A k: \u201eA sz\u201d k é d."
        assert result == expected

    def test_ref_list_after_colon_then_verse_then_continuation_no_debris(self):
        # Psalm-90 style: "fű: Jób 14,1-2; Ézs 40,6-7; 1Pt 1,24" then "6 reggel..." in same sentence.
        # Output must have colon after f, no ":;;", no stray "6".
        text = (
            "5 Elragadod őket, olyanok lesznek, mint reggelre az álom, mint a növekvő fű: Jób 14,1-2; Ézs 40,6-7; 1Pt 1,24\n"
            "6 reggel virágzik és növekszik, estére megfonnyad és elszárad."
        )
        result = get_first_letters(text)
        assert "m a n f: r v é n, e m é e." in result
        assert ":;;" not in result
        assert "f 6 r" not in result and "f6 r" not in result


class TestMainIntegration:
    """Integration tests running the script via subprocess."""

    def test_script_with_text_argument(self, tmp_path=None):
        import subprocess
        if tmp_path is None:
            import tempfile
            tmp_path = Path(tempfile.mkdtemp())
        project_root = Path(__file__).resolve().parent.parent
        result = subprocess.run(
            [sys.executable, "create_summary.py", "In the beginning.", "-o", "test_out"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "I t b." in result.stdout
        out_file = project_root / "output" / "test_out.txt"
        assert out_file.exists()
        assert out_file.read_text() == "I t b.\n"

    def test_script_with_file_input(self):
        import subprocess
        project_root = Path(__file__).resolve().parent.parent
        tests_input = project_root / "tests" / "input"
        tests_input.mkdir(parents=True, exist_ok=True)
        passage_file = tests_input / "tests_passage.txt"
        passage_file.write_text("For God so loved the world.")
        try:
            result = subprocess.run(
                [sys.executable, "create_summary.py", "-f", str(passage_file), "-o", "test_fromfile"],
                cwd=project_root,
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            assert "F G s l t w." in result.stdout
            out_file = project_root / "output" / "test_fromfile.txt"
            assert out_file.read_text() == "F G s l t w.\n"
        finally:
            passage_file.unlink(missing_ok=True)


if __name__ == "__main__":
    if pytest is not None:
        pytest.main([__file__, "-v"])
    else:
        import unittest
        # Test classes are pytest-style (no TestCase); run test_* methods manually
        failed = []
        for name in dir():
            obj = globals().get(name)
            if isinstance(obj, type) and name.startswith("Test"):
                inst = obj()
                for mname in dir(inst):
                    if mname.startswith("test_") and callable(getattr(inst, mname)):
                        try:
                            getattr(inst, mname)()
                            print(f"OK {name}.{mname}")
                        except Exception as e:
                            print(f"FAIL {name}.{mname}: {e}")
                            failed.append((name, mname))
        sys.exit(1 if failed else 0)
